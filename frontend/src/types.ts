export interface AlertItem {
  id: string;
  timestamp: number;
  created_at_iso: string;
  category: 'video_deepfake' | 'audio_deepfake' | 'financial_fraud';
  severity: 'Informational' | 'Caution' | 'High' | 'Critical';
  title: string;
  explanation: string;
  evidence: Record<string, any>;
  source: string;
  model_or_rule: string;
  confidence_score: number;
  suggested_action: string;
  acknowledged: boolean;
  dismissed: boolean;
  repetition_count: number;
}

export interface ModelInfo {
  id: string;
  name: string;
  version: string;
  source: string;
  checkpoint_available: boolean;
  status: 'Ready' | 'Loading' | 'Unavailable' | 'Error';
  license: string;
  device: string;
  input_requirements: string;
  measured_inference_ms: number;
  limitations: string;
}

export interface CaptureSources {
  monitors: Array<{
    index: number;
    name: string;
    width: number;
    height: number;
    left: number;
    top: number;
  }>;
  audio_loopback_devices: Array<{
    id: string;
    name: string;
    channels: number;
  }>;
}

export interface MonitoringStatus {
  is_monitoring: boolean;
  video_analysis_enabled: boolean;
  audio_analysis_enabled: boolean;
  fraud_analysis_enabled: boolean;
  screen_source: any;
  audio_source: string;
  frames_captured: number;
  frames_dropped: number;
  audio_chunks_captured: number;
  audio_chunks_dropped: number;
  video_frames_processed: number;
  audio_chunks_processed: number;
  transcripts_processed: number;
  recent_activity: {
    last_video_score: number;
    last_audio_score: number;
    last_fraud_risk: number;
    last_transcript: string;
  };
  last_activity_seconds_ago: number;
}

export interface PrivacyStatus {
  retention_policy_minutes: number;
  max_retention_seconds: number;
  active_temp_files: number;
  total_temp_size_bytes: number;
  total_temp_size_mb: number;
  oldest_artifact_age_seconds: number;
  auto_cleanup_active: boolean;
  temp_directory: string;
}

export interface FrameEvidence {
  timestamp_seconds: number;
  fake_score: number;
  face_detected: boolean;
  bounding_box?: [number, number, number, number];
}

export interface VideoAnalysisResult {
  status: string;
  classification: string;
  confidence_score: number;
  frames_analyzed: number;
  suspicious_frames_count: number;
  suspicious_timestamps: number[];
  frame_evidences: FrameEvidence[];
  evidence_summary: string;
  model_name: string;
  model_version: string;
  processing_duration_ms: number;
  limitations: string;
}

export interface AudioChunkEvidence {
  start_seconds: number;
  end_seconds: number;
  fake_score: number;
  is_suspicious: boolean;
}

export interface AudioAnalysisResult {
  status: string;
  classification: string;
  confidence_score: number;
  audio_duration_seconds: number;
  chunks_analyzed: number;
  suspicious_time_ranges: number[][];
  chunk_evidences: AudioChunkEvidence[];
  evidence_summary: string;
  model_name: string;
  model_version: string;
  processing_duration_ms: number;
  limitations: string;
}

export interface FraudRiskAssessment {
  is_suspicious: boolean;
  severity: string;
  risk_score: number;
  triggering_phrases: string[];
  detected_categories: string[];
  explanation: string;
  protective_action: string;
  context_type: string;
  detection_method: string;
  timestamp: number;
}

export interface MediaAnalysisResponse {
  media_filename: string;
  media_type: string;
  video_analysis?: VideoAnalysisResult;
  audio_analysis?: AudioAnalysisResult;
  transcription?: {
    status: string;
    full_text: string;
    language: string;
    language_probability: number;
    segments: Array<{ start_seconds: number; end_seconds: number; text: string }>;
    duration_seconds: number;
    processing_duration_ms: number;
  };
  fraud_assessment?: FraudRiskAssessment;
  overall_verdict: string;
  processing_time_ms: number;
}
