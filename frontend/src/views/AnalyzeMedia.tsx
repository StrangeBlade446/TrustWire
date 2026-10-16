import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileVideo,
  FileAudio,
  CheckCircle,
  AlertTriangle,
  Clock,
  ShieldAlert,
  ShieldCheck,
  Activity,
  Layers,
  ChevronDown,
  ChevronUp,
  XCircle
} from 'lucide-react';
import { api } from '../services/api';
import { MediaAnalysisResponse } from '../types';

export const AnalyzeMedia: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [progressText, setProgressText] = useState<string>('');
  const [result, setResult] = useState<MediaAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Analysis options
  const [analyzeVideo, setAnalyzeVideo] = useState(true);
  const [analyzeAudio, setAnalyzeAudio] = useState(true);
  const [analyzeFraud, setAnalyzeFraud] = useState(true);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (selectedFile: File) => {
    setError(null);
    setResult(null);

    // Validate size (max 500MB)
    if (selectedFile.size > 500 * 1024 * 1024) {
      setError("File exceeds 500MB maximum limit.");
      return;
    }

    const validExtensions = ['.mp4', '.mov', '.mkv', '.avi', '.webm', '.wav', '.mp3', '.m4a', '.flac', '.ogg'];
    const nameLower = selectedFile.name.toLowerCase();
    const hasValidExt = validExtensions.some(ext => nameLower.endsWith(ext));

    if (!hasValidExt) {
      setError(`Unsupported file extension. Allowed formats: ${validExtensions.join(', ')}`);
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const runAnalysis = async () => {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    setProgressText('Uploading and preparing media streams...');

    try {
      setProgressText('Running forensic neural network analysis (Video, Audio & Fraud)...');
      const res = await api.uploadAndAnalyzeMedia(file, {
        analyze_video_track: analyzeVideo,
        analyze_audio_track: analyzeAudio,
        analyze_fraud_track: analyzeFraud
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Media analysis failed.');
    } finally {
      setAnalyzing(false);
      setProgressText('');
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="pb-6 border-b border-border">
        <h1 className="text-2xl font-bold text-white tracking-tight">Offline Media Forensic Analysis</h1>
        <p className="text-sm text-gray-400 mt-1">
          Perform high-precision forensic inspection on recorded audio and video files. Evaluates facial anomalies, synthetic speech acoustic markers, and transcript fraud risks.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-300 text-sm">
          <XCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Zone & Config Box */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Dropzone */}
        <div className="lg:col-span-2">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
              file
                ? 'border-teal-500/50 bg-teal-500/5'
                : 'border-border hover:border-teal-500/30 bg-panel hover:bg-panel/80'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
              className="hidden"
              accept=".mp4,.mov,.mkv,.avi,.webm,.wav,.mp3,.m4a,.flac,.ogg"
            />
            <UploadCloud className="w-12 h-12 text-teal-400/80 mx-auto mb-4" />
            {file ? (
              <div className="space-y-2">
                <div className="text-base font-semibold text-white">{file.name}</div>
                <div className="text-xs text-gray-400 font-mono">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • {file.type || 'Media File'}
                </div>
                <div className="text-xs text-teal-400 font-medium pt-2">Click or drag another file to replace</div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-base font-semibold text-white">Choose a media file or drag & drop here</div>
                <p className="text-xs text-gray-400">
                  Video: MP4, MOV, MKV, AVI, WebM • Audio: WAV, MP3, M4A, FLAC (Max 500MB)
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Forensic Execution Options */}
        <div className="p-6 rounded-2xl border border-border bg-panel space-y-6">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-teal-400" />
            Inspection Parameters
          </h3>

          <div className="space-y-4 text-xs">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={analyzeVideo}
                onChange={(e) => setAnalyzeVideo(e.target.checked)}
                className="w-4 h-4 rounded text-teal-500 focus:ring-teal-400 border-border bg-surface mt-0.5"
              />
              <div>
                <span className="font-semibold text-white block">Analyze Visual Frames (ViT)</span>
                <span className="text-gray-400">Samples frames and tests facial regions for AI generative artifacts.</span>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={analyzeAudio}
                onChange={(e) => setAnalyzeAudio(e.target.checked)}
                className="w-4 h-4 rounded text-teal-500 focus:ring-teal-400 border-border bg-surface mt-0.5"
              />
              <div>
                <span className="font-semibold text-white block">Analyze Audio Track (Wav2Vec2)</span>
                <span className="text-gray-400">Evaluates speech track for synthetic voice or cloning anomalies.</span>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={analyzeFraud}
                onChange={(e) => setAnalyzeFraud(e.target.checked)}
                className="w-4 h-4 rounded text-teal-500 focus:ring-teal-400 border-border bg-surface mt-0.5"
              />
              <div>
                <span className="font-semibold text-white block">Speech Transcription & Fraud Rules</span>
                <span className="text-gray-400">Transcribes dialogue and evaluates credential theft, urgency, and extortion.</span>
              </div>
            </label>
          </div>

          <button
            onClick={runAnalysis}
            disabled={!file || analyzing}
            className={`w-full py-3 rounded-xl font-semibold text-sm transition-all shadow-lg ${
              !file || analyzing
                ? 'bg-surface text-gray-500 cursor-not-allowed border border-border'
                : 'bg-teal-500 hover:bg-teal-400 text-black shadow-teal-500/20'
            }`}
          >
            {analyzing ? (
              <span className="flex items-center justify-center gap-2">
                <Activity className="w-4 h-4 animate-spin" />
                Analyzing Media...
              </span>
            ) : (
              'Run Multi-Vector Inspection'
            )}
          </button>

          {analyzing && (
            <p className="text-xs text-center text-teal-300 font-mono animate-pulse">
              {progressText}
            </p>
          )}
        </div>
      </div>

      {/* Structured Forensic Results Report */}
      {result && (
        <div className="space-y-6 pt-4 border-t border-border">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Forensic Assessment Report</span>
              <h2 className="text-xl font-bold text-white mt-1">{result.media_filename}</h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400 font-mono">
                Duration: {(result.processing_time_ms / 1000).toFixed(2)}s
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                result.overall_verdict.includes('Suspicious') || result.overall_verdict.includes('Risk')
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  : 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
              }`}>
                {result.overall_verdict}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Video Track Result Card */}
            {result.video_analysis && (
              <div className="p-6 rounded-2xl border border-border bg-panel space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileVideo className="w-5 h-5 text-teal-400" />
                    <span className="font-semibold text-sm text-white">Visual Authenticity</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                    result.video_analysis.classification === 'Potentially manipulated'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : result.video_analysis.classification === 'Likely authentic'
                      ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
                      : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                  }`}>
                    {result.video_analysis.classification}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-gray-400">
                    <span>Analyzed Frames:</span>
                    <span className="font-mono text-white">{result.video_analysis.frames_analyzed}</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Suspicious Frames:</span>
                    <span className="font-mono text-white">{result.video_analysis.suspicious_frames_count}</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Aggregate Score:</span>
                    <span className="font-mono text-white">{(result.video_analysis.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <p className="text-xs text-gray-300 pt-2 border-t border-border/40">
                  {result.video_analysis.evidence_summary}
                </p>

                {result.video_analysis.suspicious_timestamps.length > 0 && (
                  <div className="text-[11px] text-gray-400">
                    Anomalies at: {result.video_analysis.suspicious_timestamps.map(t => `${t.toFixed(1)}s`).join(', ')}
                  </div>
                )}
              </div>
            )}

            {/* Audio Track Result Card */}
            {result.audio_analysis && (
              <div className="p-6 rounded-2xl border border-border bg-panel space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileAudio className="w-5 h-5 text-cyan-400" />
                    <span className="font-semibold text-sm text-white">Audio Authenticity</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                    result.audio_analysis.classification === 'Potentially synthetic'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : result.audio_analysis.classification === 'Likely authentic'
                      ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
                      : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                  }`}>
                    {result.audio_analysis.classification}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-gray-400">
                    <span>Duration:</span>
                    <span className="font-mono text-white">{result.audio_analysis.audio_duration_seconds}s</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Acoustic Chunks:</span>
                    <span className="font-mono text-white">{result.audio_analysis.chunks_analyzed}</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Aggregate Fake Prob:</span>
                    <span className="font-mono text-white">{(result.audio_analysis.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <p className="text-xs text-gray-300 pt-2 border-t border-border/40">
                  {result.audio_analysis.evidence_summary}
                </p>

                {result.audio_analysis.suspicious_time_ranges.length > 0 && (
                  <div className="text-[11px] text-gray-400">
                    Suspicious ranges: {result.audio_analysis.suspicious_time_ranges.map(r => `[${r[0]}s - ${r[1]}s]`).join(', ')}
                  </div>
                )}
              </div>
            )}

            {/* Fraud & Social Engineering Result Card */}
            {result.fraud_assessment && (
              <div className="p-6 rounded-2xl border border-border bg-panel space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-amber-400" />
                    <span className="font-semibold text-sm text-white">Fraud & Coercion</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                    result.fraud_assessment.is_suspicious
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
                  }`}>
                    {result.fraud_assessment.severity}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-gray-400">
                    <span>Risk Index:</span>
                    <span className="font-mono text-white">{(result.fraud_assessment.risk_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Categories:</span>
                    <span className="text-gray-300 truncate">{result.fraud_assessment.detected_categories.join(', ') || 'None'}</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Trigger Words:</span>
                    <span className="text-gray-300 truncate">{result.fraud_assessment.triggering_phrases.join(', ') || 'None'}</span>
                  </div>
                </div>

                <p className="text-xs text-gray-300 pt-2 border-t border-border/40">
                  {result.fraud_assessment.explanation}
                </p>

                <div className="p-2.5 rounded bg-surface border border-border text-xs text-amber-300">
                  {result.fraud_assessment.protective_action}
                </div>
              </div>
            )}
          </div>

          {/* Transcript Excerpt Viewer */}
          {result.transcription && result.transcription.full_text && (
            <div className="p-6 rounded-2xl border border-border bg-panel space-y-3">
              <h3 className="text-sm font-semibold text-white">Decoded Speech Transcript</h3>
              <div className="p-4 rounded-xl bg-surface border border-border text-xs text-gray-300 leading-relaxed max-h-48 overflow-y-auto">
                {result.transcription.full_text}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
