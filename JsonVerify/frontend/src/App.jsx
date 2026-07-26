import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FolderOpen,
  Play,
  Copy,
  FolderSearch,
  Trash2,
  Loader2,
  CheckCircle,
  FileText,
  GitPullRequest,
  AlertCircle
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [filePath, setFilePath] = useState('');
  const [dirPath, setDirPath] = useState('');
  const [status, setStatus] = useState('Prêt');
  const [stats, setStats] = useState({ total: 0, ok: 0, errors: 0, skipped: 0 });
  const [logs, setLogs] = useState([]);
  const [githubText, setGithubText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(-1);
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const log = (message, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time, message, type }]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const addStatus = (msg) => {
    setStatus(msg);
    log(msg, 'info');
  };

  const loadFile = async (file) => {
    try {
      const text = await file.text();
      const jsonData = JSON.parse(text);
      
      const res = await fetch(`${API_BASE}/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          filename: file.name,
          data: jsonData 
        })
      });
      const data = await res.json();
      if (res.ok) {
        setFilePath(data.filename);
        addStatus(`${data.filename} · ${data.count} dialogues chargés`);
        setProgress(0);
        setStats({ total: 0, ok: 0, errors: 0, skipped: 0 });
        setGithubText('');
      } else {
        addStatus(`Erreur : ${data.detail}`);
        log(`Erreur : ${data.detail}`, 'error');
      }
    } catch (error) {
      addStatus(`Erreur : ${error.message}`);
      log(`Erreur : ${error.message}`, 'error');
    }
  };

  const verifyFile = async () => {
    if (!filePath) {
      addStatus('Aucun fichier chargé');
      return;
    }
    setIsLoading(true);
    setProgress(0);
    clearLogs();
    log(`Vérification du fichier : ${filePath}`, 'info');
    try {
      const res = await fetch(`${API_BASE}/verify`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setStats({ total: data.total, ok: data.ok, errors: data.errors, skipped: data.skipped });
        data.logs.forEach(line => {
          if (line.startsWith('ERROR') || line.startsWith('CRASH')) {
            log(line, 'error');
          } else if (line.startsWith('OK')) {
            log(line, 'success');
          } else {
            log(line, 'info');
          }
        });
        setProgress(1);
        if (data.errors > 0) {
          addStatus(`${data.errors} erreur(s) détectée(s)`);
          if (data.github_text) setGithubText(data.github_text);
        } else {
          addStatus('Vérification terminée – aucune erreur');
        }
      } else {
        addStatus(`Erreur : ${data.detail}`);
        log(`Erreur : ${data.detail}`, 'error');
      }
    } catch (error) {
      addStatus(`Erreur : ${error.message}`);
      log(`Erreur : ${error.message}`, 'error');
    }
    setIsLoading(false);
  };

  const processDirectory = async () => {
    if (!dirPath) {
      addStatus('Aucun dossier sélectionné');
      return;
    }
    setIsLoading(true);
    setProgress(0);
    clearLogs();
    setStats({ total: 0, ok: 0, errors: 0, skipped: 0 });
    log(`Mode Dossier : ${dirPath}`, 'info');

    try {
      const res = await fetch(`${API_BASE}/process_directory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dir_path: dirPath })
      });
      const data = await res.json();
      if (res.ok) {
        data.results.forEach((result, index) => {
          setProgress((index + 1) / data.total_files);
          if (result.status === 'error') {
            log(`${result.file} (${result.error_count} erreur(s))`, 'error');
            result.logs?.forEach(line => {
              if (line.startsWith('ERROR') || line.startsWith('CRASH')) {
                log(`  ${line}`, 'error');
              }
            });
          } else {
            log(`${result.file}`, 'success');
          }
        });
        setStats({ total: data.total_files, ok: data.ok_files, errors: data.error_files, skipped: 0 });
        addStatus(`Terminé – ${data.ok_files} OK, ${data.error_files} erreur(s)`);
        log(`Résumé : ${data.ok_files}/${data.total_files} fichiers valides`, 'success');
      } else {
        addStatus(`Erreur : ${data.detail}`);
        log(`Erreur : ${data.detail}`, 'error');
      }
    } catch (error) {
      addStatus(`Erreur : ${error.message}`);
      log(`Erreur : ${error.message}`, 'error');
    }
    setIsLoading(false);
  };

  const handleFileSelect = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        loadFile(file);
      }
    };
    input.click();
  };

  const handleDirSelect = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    input.onchange = (e) => {
      const files = e.target.files;
      if (files.length > 0) {
        const firstFile = files[0];
        const path = firstFile.path || firstFile.webkitRelativePath;
        const dir = path.split('/').slice(0, -1).join('/');
        setDirPath(dir);
        addStatus(`Dossier sélectionné : ${dir}`);
      }
    };
    input.click();
  };

  const copyGithubIssue = async () => {
    if (!githubText) {
      try {
        const res = await fetch(`${API_BASE}/github`);
        const data = await res.json();
        if (res.ok) {
          await navigator.clipboard.writeText(data.text);
          addStatus('Issue GitHub copiée');
        }
      } catch (error) {
        log(`Erreur : ${error.message}`, 'error');
      }
    } else {
      await navigator.clipboard.writeText(githubText);
      addStatus('Issue GitHub copiée');
    }
  };

  return (
    <div className="min-h-screen text-white p-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto mb-8"
      >
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-300 to-cyan-100 mb-2 text-center">
          JsonVerify
        </h1>
        <p className="text-center text-blue-200/60 text-sm">Vérificateur de dialogues JSON</p>
      </motion.div>

      {/* Main Container */}
      <div className="max-w-6xl mx-auto">
        {/* Status Panel */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel rounded-2xl p-6 mb-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse" />
              <span className="text-lg">{status}</span>
            </div>
            {isLoading && <Loader2 size={20} className="animate-spin text-blue-400" />}
          </div>
        </motion.div>

        {/* Actions Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Fichier Unique */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-panel rounded-2xl p-6"
          >
            <h3 className="text-sm font-semibold uppercase tracking-wider text-blue-300 mb-4">① Fichier unique</h3>
            <div className="flex flex-wrap gap-2">
              <button onClick={handleFileSelect} className="glass-button">
                <FolderOpen size={18} /> Charger JSON
              </button>
              <button onClick={verifyFile} disabled={isLoading || !filePath} className="glass-button-success">
                {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
                Vérifier
              </button>
              <button onClick={copyGithubIssue} disabled={!githubText && !filePath} className="glass-button-secondary">
                <Copy size={18} /> Copier Issue
              </button>
            </div>
            {filePath && <div className="text-xs text-blue-200/50 mt-3 truncate">Fichier: {filePath}</div>}
          </motion.div>

          {/* Dossier Entier */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-panel rounded-2xl p-6"
          >
            <h3 className="text-sm font-semibold uppercase tracking-wider text-blue-300 mb-4">② Dossier complet</h3>
            <div className="flex flex-wrap gap-2">
              <button onClick={handleDirSelect} className="glass-button-secondary">
                <FolderSearch size={18} /> Sélectionner
              </button>
              <button onClick={processDirectory} disabled={isLoading || !dirPath} className="glass-button">
                {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
                Vérifier
              </button>
            </div>
            {dirPath && <div className="text-xs text-blue-200/50 mt-3 truncate">Dossier: {dirPath}</div>}
          </motion.div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="stat-card text-center">
            <div className="text-3xl font-bold text-cyan-400 mb-1">{stats.total}</div>
            <div className="text-xs font-medium uppercase text-blue-300/60">Dialogues</div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="stat-card text-center">
            <div className="text-3xl font-bold text-emerald-400 mb-1">{stats.ok}</div>
            <div className="text-xs font-medium uppercase text-blue-300/60">OK</div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="stat-card text-center">
            <div className="text-3xl font-bold text-red-400 mb-1">{stats.errors}</div>
            <div className="text-xs font-medium uppercase text-blue-300/60">Erreurs</div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="stat-card text-center">
            <div className="text-3xl font-bold text-gray-400 mb-1">{stats.skipped}</div>
            <div className="text-xs font-medium uppercase text-blue-300/60">Skippées</div>
          </motion.div>
        </div>

        {/* Progress Bar */}
        {progress >= 0 && (
          <div className="w-full bg-white/5 rounded-full h-2 mb-6 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress * 100}%` }}
              transition={{ duration: 0.3 }}
              className="bg-gradient-to-r from-blue-500 to-cyan-400 h-2"
            />
          </div>
        )}

        {/* Console/Logs */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="glass-panel rounded-2xl overflow-hidden"
        >
          <div className="flex items-center justify-between px-6 py-3 border-b border-white/10">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-300">Console / Résultat</span>
            <button
              onClick={clearLogs}
              className="flex items-center gap-1.5 px-3 py-1 text-xs text-blue-300 hover:text-white hover:bg-white/10 rounded transition-all"
            >
              <Trash2 size={14} /> Effacer
            </button>
          </div>
          <div className="p-6 font-mono text-sm max-h-96 overflow-y-auto bg-black/20">
            {logs.length === 0 ? (
              <span className="text-blue-300/40">En attente d'une action...</span>
            ) : (
              logs.map((log, i) => (
                <div
                  key={i}
                  className={`${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-emerald-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    'text-blue-300'
                  }`}
                >
                  <span className="text-blue-500/50">[{log.time}]</span> {log.message}
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-8 text-center"
        >
          <a 
            href="https://github.com/Garloulou/JsonVerify"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-blue-300 text-sm transition-all"
          >
            <GitPullRequest size={16} />
            GitHub Repository
          </a>
          <p className="text-blue-300/40 text-xs mt-3">CC BY-NC-SA 4.0</p>
        </motion.div>
      </div>
    </div>
  );
}

export default App;