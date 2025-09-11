import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import { 
  Globe, Languages, FileText, Users, Shield, Zap, 
  Mic, MicOff, Volume2, Copy, Download, Upload, Camera, 
  Settings, Bell, User, Search, Plus, Send, Pause, 
  Video, PhoneOff, Share, UserPlus, FolderOpen, RefreshCw, Trash2,
  AlertCircle
} from 'lucide-react';
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { Separator } from "./components/ui/separator";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Suppress ResizeObserver errors
    if (error.message && error.message.includes('ResizeObserver')) {
      this.setState({ hasError: false });
      return;
    }
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary-icon">
            <AlertCircle className="h-6 w-6" />
          </div>
          <h3 className="text-heading-3 mb-2">Something went wrong</h3>
          <p className="text-body mb-4">
            We're sorry, but something unexpected happened. Please try refreshing the page.
          </p>
          <Button 
            onClick={() => {
              this.setState({ hasError: false, error: null, errorInfo: null });
              window.location.reload();
            }}
            className="btn-primary"
          >
            Refresh Page
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Expanded language options covering major world languages
const LANGUAGES = {
  eng: "English",
  spa: "Spanish (Español)", 
  heb: "Hebrew (עברית)",
  ara: "Arabic (العربية)",
  fra: "French (Français)",
  deu: "German (Deutsch)",
  ita: "Italian (Italiano)",
  por: "Portuguese (Português)",
  rus: "Russian (Русский)",
  chi: "Chinese (中文)",
  jpn: "Japanese (日本語)",
  kor: "Korean (한국어)",
  hin: "Hindi (हिन्दी)",
  tur: "Turkish (Türkçe)",
  pol: "Polish (Polski)",
  nld: "Dutch (Nederlands)",
  swe: "Swedish (Svenska)",
  nor: "Norwegian (Norsk)",
  dan: "Danish (Dansk)",
  fin: "Finnish (Suomi)",
  hun: "Hungarian (Magyar)",
  ces: "Czech (Čeština)",
  slk: "Slovak (Slovenčina)",
  ron: "Romanian (Română)",
  bul: "Bulgarian (Български)",
  hrv: "Croatian (Hrvatski)",
  srp: "Serbian (Српски)",
  ukr: "Ukrainian (Українська)",
  ell: "Greek (Ελληνικά)",
  tha: "Thai (ไทย)",
  vie: "Vietnamese (Tiếng Việt)",
  ind: "Indonesian (Bahasa Indonesia)",
  msa: "Malay (Bahasa Melayu)",
  tgl: "Filipino (Tagalog)",
  swa: "Swahili (Kiswahili)",
  amh: "Amharic (አማርኛ)",
  ben: "Bengali (বাংলা)",
  guj: "Gujarati (ગુજરાતી)",
  pan: "Punjabi (ਪੰਜਾਬੀ)",
  tam: "Tamil (தமிழ்)",
  tel: "Telugu (తెలుగు)",
  mal: "Malayalam (മലയാളം)",
  kan: "Kannada (ಕನ್ನಡ)",
  mar: "Marathi (मराठी)",
  nep: "Nepali (नेपाली)",
  sin: "Sinhala (සිංහල)",
  mya: "Burmese (မြန်မာ)",
  khm: "Khmer (ខ្មែរ)",
  lao: "Lao (ລາວ)",
  kat: "Georgian (ქართული)",
  arm: "Armenian (Հայերեն)",
  aze: "Azerbaijani (Azərbaycan)",
  kaz: "Kazakh (Қазақ)",
  kir: "Kyrgyz (Кыргыз)",
  uzb: "Uzbek (O'zbek)",
  tgk: "Tajik (Тоҷикӣ)",
  mon: "Mongolian (Монгол)",
  bod: "Tibetan (བོད་ཡིག)",
  uig: "Uyghur (ئۇيغۇرچە)"
};

const INDUSTRIES = {
  general: "General",
  healthcare: "Healthcare",
  construction: "Construction", 
  banking: "Banking & Finance",
  government: "Government",
  education: "Education",
  legal: "Legal",
  technology: "Technology",
  manufacturing: "Manufacturing",
  retail: "Retail & E-commerce",
  hospitality: "Hospitality & Tourism",
  transportation: "Transportation & Logistics",
  energy: "Energy & Utilities",
  media: "Media & Entertainment",
  consulting: "Consulting",
  insurance: "Insurance",
  realEstate: "Real Estate",
  agriculture: "Agriculture",
  pharmaceutical: "Pharmaceutical",
  automotive: "Automotive"
};

function App() {
  const [activeTab, setActiveTab] = useState("translate");
  const [sourceText, setSourceText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [sourceLang, setSourceLang] = useState(() => {
    try {
      const saved = localStorage.getItem('comprende-settings');
      const settings = saved ? JSON.parse(saved) : {};
      return settings.defaultSourceLang || 'auto';
    } catch (error) {
      return 'auto';
    }
  });
  const [targetLang, setTargetLang] = useState(() => {
    try {
      const saved = localStorage.getItem('comprende-settings');
      const settings = saved ? JSON.parse(saved) : {};
      return settings.defaultTargetLang || 'eng';
    } catch (error) {
      return 'eng';
    }
  });
  const [context, setContext] = useState("general");
  const [industry, setIndustry] = useState("general");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [file, setFile] = useState(null);
  const [documentResult, setDocumentResult] = useState(null);
  const [translationHistory, setTranslationHistory] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const [users, setUsers] = useState([]);
  // User authentication state
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('comprende-user');
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      return null;
    }
  });
  const [showLogin, setShowLogin] = useState(!currentUser);
  const [meetings, setMeetings] = useState([]);
  const [sharedFiles, setSharedFiles] = useState([]);
  // WebRTC and WebSocket state
  const [localStream, setLocalStream] = useState(null);
  const [remoteStreams, setRemoteStreams] = useState(new Map()); // Map of user_id -> MediaStream
  const [peerConnections, setPeerConnections] = useState(new Map()); // Map of user_id -> RTCPeerConnection
  const [websocket, setWebsocket] = useState(null);
  const [currentMeetingId, setCurrentMeetingId] = useState(null);
  const [connectedUsers, setConnectedUsers] = useState([]);

  // WebRTC configuration
  const rtcConfiguration = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
  };
  const [notifications, setNotifications] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  // Teams and file sharing state
  const [teams, setTeams] = useState([]);
  const [currentTeam, setCurrentTeam] = useState(null);
  const [teamFiles, setTeamFiles] = useState([]);
  const [showTeamCreator, setShowTeamCreator] = useState(false);
  const [showTeamJoiner, setShowTeamJoiner] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedTeamForFiles, setSelectedTeamForFiles] = useState(null);
  
  // Settings state with localStorage persistence
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('comprende-settings');
      return saved ? JSON.parse(saved) : {
        voiceInputEnabled: true,
        voiceOutputEnabled: true,
        autoTranslateVoice: false,
        defaultSourceLang: 'auto',
        defaultTargetLang: 'eng'
      };
    } catch (error) {
      console.error('Failed to load settings:', error);
      return {
        voiceInputEnabled: true,
        voiceOutputEnabled: true,
        autoTranslateVoice: false,
        defaultSourceLang: 'auto',
        defaultTargetLang: 'eng'
      };
    }
  });

  // Save settings to localStorage whenever settings change
  useEffect(() => {
    try {
      localStorage.setItem('comprende-settings', JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [settings]);

  // Save user to localStorage when it changes
  useEffect(() => {
    if (currentUser) {
      try {
        localStorage.setItem('comprende-user', JSON.stringify(currentUser));
        setShowLogin(false);
        // Initialize WebSocket connection when user logs in
        setTimeout(() => {
          initializeWebSocket();
        }, 1000);
        // Load user teams
        setTimeout(() => {
          loadUserTeams();
        }, 1500);
      } catch (error) {
        console.error('Failed to save user:', error);
      }
    } else {
      localStorage.removeItem('comprende-user');
      setShowLogin(true);
      // Close WebSocket connection when user logs out
      if (websocket) {
        websocket.close();
        setWebsocket(null);
      }
      // Clear teams data
      setTeams([]);
      setCurrentTeam(null);
      setTeamFiles([]);
    }
  }, [currentUser]);

  const loginUser = async (userData) => {
    try {
      // Create or get user from backend
      const response = await axios.post(`${BACKEND_URL}/api/users`, {
        username: userData.name,
        email: userData.email,
        preferred_languages: [targetLang, sourceLang]
      });
      
      // Generate Gravatar URL if no custom avatar
      let avatarUrl = userData.avatar;
      if (!avatarUrl || avatarUrl === "👤") {
        const emailHash = await generateGravatarHash(userData.email);
        avatarUrl = `https://www.gravatar.com/avatar/${emailHash}?d=identicon&s=40`;
      }
      
      const user = {
        id: response.data.id,
        name: userData.name,
        email: userData.email,
        avatar: avatarUrl,
        joinedAt: new Date().toISOString()
      };
      
      setCurrentUser(user);
      toast.success(`Welcome, ${user.name}!`);
      
    } catch (error) {
      console.error('Login failed:', error);
      // Fallback to local user creation
      let avatarUrl = userData.avatar;
      if (!avatarUrl || avatarUrl === "👤") {
        const emailHash = await generateGravatarHash(userData.email);
        avatarUrl = `https://www.gravatar.com/avatar/${emailHash}?d=identicon&s=40`;
      }
      
      const user = {
        id: `user-${Date.now()}`,
        name: userData.name,
        email: userData.email,
        avatar: avatarUrl,
        joinedAt: new Date().toISOString()
      };
      setCurrentUser(user);
      toast.success(`Welcome, ${user.name}! (Local session)`);
    }
  };

  const generateGravatarHash = async (email) => {
    const trimmedEmail = email.toLowerCase().trim();
    const encoder = new TextEncoder();
    const data = encoder.encode(trimmedEmail);
    const hashBuffer = await crypto.subtle.digest('MD5', data).catch(() => {
      // Fallback if MD5 not available
      let hash = 0;
      for (let i = 0; i < trimmedEmail.length; i++) {
        const char = trimmedEmail.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return hash.toString(16);
    });
    
    if (typeof hashBuffer === 'string') return hashBuffer;
    
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  const handleAvatarUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 1024 * 1024) { // 1MB limit
        toast.error("Avatar image must be smaller than 1MB");
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const newUser = { ...currentUser, avatar: e.target.result };
        setCurrentUser(newUser);
        toast.success("Avatar updated successfully!");
      };
      reader.readAsDataURL(file);
    }
  };

  const speakText = (text, language = 'en') => {
    if (!settings.voiceOutputEnabled) {
      toast.error("Voice output is disabled in settings");
      return;
    }

    if (!('speechSynthesis' in window)) {
      toast.error("Text-to-speech not supported in this browser");
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Map language codes to speech synthesis language codes
    const voiceLanguageMatrix = {
      'eng': 'en-US',
      'spa': 'es-ES',
      'fra': 'fr-FR',
      'deu': 'de-DE',
      'heb': 'he-IL',
      'ara': 'ar-SA',
      'ita': 'it-IT',
      'por': 'pt-PT',
      'rus': 'ru-RU',
      'chi': 'zh-CN',
      'jpn': 'ja-JP',
      'kor': 'ko-KR',
      'hin': 'hi-IN',
      'tur': 'tr-TR',
      'pol': 'pl-PL',
      'nld': 'nl-NL',
      'swe': 'sv-SE',
      'nor': 'no-NO',
      'dan': 'da-DK',
      'fin': 'fi-FI'
    };

    utterance.lang = voiceLanguageMatrix[language] || 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = () => {
      setIsSpeaking(true);
      toast.success(`🔊 Playing in ${LANGUAGES[language] || 'English'}...`);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      toast.error(`Speech playback failed: ${event.error}`);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      console.log('Speech synthesis finished');
    };

    try {
      window.speechSynthesis.speak(utterance);
    } catch (error) {
      console.error('Failed to start speech synthesis:', error);
      toast.error("Failed to start speech playback");
    }
  };

  const downloadFileFormatted = async (content, filename, originalFormat = 'txt') => {
    try {
      // Detect browser type for better error handling
      const isBrave = navigator.brave && await navigator.brave.isBrave();
      
      // Use backend formatted download endpoint
      const response = await axios.post(`${BACKEND_URL}/api/documents/download-formatted`, {
        content: content,
        filename: filename,
        format: originalFormat
      }, {
        responseType: 'blob'
      });

      // Create download link from blob response
      const blob = new Blob([response.data]);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      // For better browser compatibility
      link.style.display = 'none';
      document.body.appendChild(link);
      
      // Trigger download
      link.click();
      
      // Cleanup
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, 100);
      
      // Success message with format info
      const formatName = originalFormat.toUpperCase();
      if (isBrave) {
        toast.success(`📁 ${formatName} file download started! Check Brave's download icon if not visible.`, { duration: 5000 });
      } else {
        toast.success(`📁 ${formatName} file "${filename}" downloaded in original format!`);
      }
      
    } catch (error) {
      console.error('Formatted download failed:', error);
      // Fallback to regular text download
      await downloadFile(content, filename.replace(/\.(pdf|xlsx|xls)$/i, '.txt'));
      toast.info("Downloaded as text file (original format conversion failed)");
    }
  };

  // Check if user is accessing a meeting via URL
  useEffect(() => {
    const path = window.location.pathname;
    const meetingMatch = path.match(/\/meeting\/(.+)/);
    
    if (meetingMatch) {
      const meetingId = meetingMatch[1];
      joinMeetingById(meetingId);
    }
  }, []);

  const joinMeetingById = async (meetingId) => {
    try {
      // Try to fetch meeting from backend
      const response = await axios.get(`${BACKEND_URL}/api/meetings/${meetingId}`);
      
      if (response.data) {
        const meeting = response.data;
        
        // Add user to meeting participants if not already there
        if (!meeting.participants.includes(currentUser?.name || "Anonymous User")) {
          meeting.participants.push(currentUser?.name || "Anonymous User");
          
          // Update meeting in backend
          await axios.put(`${BACKEND_URL}/api/meetings/${meetingId}`, {
            participants: meeting.participants
          });
        }
        
        // Add meeting to local state if not already there
        setMeetings(prev => {
          const existing = prev.find(m => m.id === meetingId);
          if (!existing) {
            return [...prev, meeting];
          }
          return prev;
        });
        
        // Switch to collaborate tab and auto-join
        setActiveTab("collaborate");
        toast.success(`🎥 Joined meeting: ${meeting.name}`);
        
        
      }
    } catch (error) {
      console.error('Failed to join meeting:', error);
      toast.error(`❌ Meeting not found or expired. Meeting ID: ${meetingId}`);
    }
  };

  const logoutUser = () => {
    setCurrentUser(null);
    localStorage.removeItem('comprende-user');
    // Clear any active meetings/streams
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      setLocalStream(null);
    }
    setMeetings([]);
    toast.success("Logged out successfully");
  };
  
  // Voice recognition refs
  const recognitionRef = useRef(null);
  const speechSynthRef = useRef(null);

  // Check system health on load
  useEffect(() => {
    checkHealth();
    loadTranslationHistory();
    initializeVoiceRecognition();
    loadUserData();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API}/health`);
      setHealthStatus(response.data);
    } catch (error) {
      console.error("Health check failed:", error);
      toast.error("System health check failed");
    }
  };

  const loadTranslationHistory = async () => {
    try {
      const response = await axios.get(`${API}/translations/history?limit=10`);
      setTranslationHistory(response.data);
    } catch (error) {
      console.error("Failed to load history:", error);
    }
  };

  const loadUserData = () => {
    // Set up mock team members and notifications
    setUsers([
      { id: "user-1", name: "Demo User", status: "online", avatar: "👤" },
      { id: "user-2", name: "Alice Johnson", status: "online", avatar: "👩" },
      { id: "user-3", name: "Bob Smith", status: "away", avatar: "👨" },
      { id: "user-4", name: "Carol Davis", status: "offline", avatar: "👩‍💼" }
    ]);

    setNotifications([
      { id: 1, type: "translation", message: "New translation request from Alice", time: "2 min ago" },
      { id: 2, type: "meeting", message: "Team meeting starting in 15 minutes", time: "15 min ago" },
      { id: 3, type: "file", message: "Document shared by Bob", time: "1 hour ago" }
    ]);
  };

  const initializeVoiceRecognition = () => {
    if (!settings.voiceInputEnabled) return;

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        toast.error("Voice recognition not supported in this browser. Please use Chrome, Edge, or Safari.");
        return;
      }

      // Voice recognition is now handled by the startVoiceRecognition function
      console.log('Voice recognition initialized');

    } catch (error) {
      console.error('Failed to initialize voice recognition:', error);
      toast.error("Failed to initialize voice recognition");
    }
  };

  const handleTranslate = async () => {
    if (!sourceText.trim()) {
      toast.error("Please enter text to translate");
      return;
    }

    setIsLoading(true);
    setTranslatedText("");
    
    try {
      console.log("Starting translation request...");
      const requestBody = {
        text: sourceText,
        source_language: sourceLang === "auto" ? null : sourceLang,
        target_language: targetLang,
        context: context,
        industry: industry
      };
      
      const response = await axios.post(`${API}/translate`, requestBody, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000
      });

      if (response.data && response.data.translated_text) {
        setTranslatedText(response.data.translated_text);
        if (response.data.source_language) {
          setDetectedLanguage(response.data.source_language);
          // If using auto-detect, update the source language for better UX
          if (sourceLang === 'auto') {
            // Only update display, don't change the actual sourceLang value
            setDetectedLanguage(response.data.source_language);
          }
        }
        toast.success(`Translation completed with ${(response.data.confidence * 100).toFixed(1)}% confidence`);
        loadTranslationHistory();
      } else {
        toast.error("Invalid response from translation service");
      }
    } catch (error) {
      console.error("Translation failed:", error);
      handleApiError(error, "Translation failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleApiError = (error, defaultMessage) => {
    if (error.response) {
      toast.error(`${defaultMessage}: ${error.response.data?.detail || error.response.statusText}`);
    } else if (error.request) {
      toast.error(`${defaultMessage}: No response from server`);
    } else {
      toast.error(`${defaultMessage}: ${error.message}`);
    }
  };

  const handleDocumentUpload = async () => {
    if (!file) {
      toast.error("Please select a file to process");
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("languages", "eng,heb,ara,spa,fra");
    formData.append("translate_to", targetLang);

    try {
      const response = await axios.post(`${API}/documents/process`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000
      });

      setDocumentResult(response.data);
      setUploadedFiles(prev => [...prev, { ...response.data, file: file }]);
      toast.success("Document processed successfully");
    } catch (error) {
      console.error("Document processing failed:", error);
      if (error.code === 'EACCES' || error.message.includes('permission')) {
        toast.error("File could not be processed due to file protection or permissions");
      } else {
        handleApiError(error, "Document processing failed");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      // Check if we have clipboard API support
      if (navigator.clipboard && window.isSecureContext) {
        // Try to use the modern Clipboard API
        await navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard!");
      } else {
        // Fallback method for older browsers or non-secure contexts
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          const successful = document.execCommand('copy');
          if (successful) {
            toast.success("Copied to clipboard!");
          } else {
            throw new Error('Copy command failed');
          }
        } catch (err) {
          // If all else fails, show the text to copy manually
          toast.error(`Copy failed. Please copy manually: ${text.substring(0, 50)}...`);
        }
        
        document.body.removeChild(textArea);
      }
    } catch (error) {
      console.error('Clipboard operation failed:', error);
      
      // For Brave and other privacy-focused browsers
      if (error.name === 'NotAllowedError') {
        toast.error("📋 Clipboard access denied. Please allow clipboard permissions in browser settings.");
      } else {
        // Show a manual copy dialog
        const shortText = text.length > 100 ? text.substring(0, 100) + '...' : text;
        toast.error(`Copy failed. Text: ${shortText}`);
      }
    }
  };



  // Voice input handling
  const toggleVoiceInput = () => {
    if (!isListening) {
      startVoiceRecognition();
    } else {
      stopVoiceRecognition();
    }
  };

  const startVoiceRecognition = () => {
    // Check if voice input is enabled in settings
    if (!settings.voiceInputEnabled) {
      toast.error("Voice input is disabled in settings");
      return;
    }

    // Check for browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error("Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    
    // Set language based on source language selection
    const recognitionLang = getVoiceLanguageCode(sourceLang);
    recognition.lang = recognitionLang;

    recognition.onstart = () => {
      setIsListening(true);
      const langName = sourceLang === 'auto' ? 'Auto-detect' : (LANGUAGES[sourceLang] || 'English');
      toast.success(`🎤 Listening in ${langName}...`);
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // Update the text with final result
      if (finalTranscript) {
        setSourceText(prev => prev + finalTranscript);
        setIsListening(false);
        toast.success(`✅ Voice captured: "${finalTranscript.substring(0, 50)}${finalTranscript.length > 50 ? '...' : ''}"`);
        
        // Auto-translate if enabled
        if (settings.autoTranslateVoice) {
          setTimeout(() => handleTranslate(), 500);
        }
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      let errorMessage = "Speech recognition error";
      switch (event.error) {
        case 'no-speech':
          errorMessage = "No speech detected. Please try speaking again.";
          break;
        case 'audio-capture':
          errorMessage = "Microphone not found. Please check your microphone connection.";
          break;
        case 'not-allowed':
          errorMessage = "Microphone permission denied. Please allow microphone access in your browser settings.";
          break;
        case 'network':
          errorMessage = "Network error occurred. Please check your internet connection and try again.";
          break;
        case 'language-not-supported':
          errorMessage = `Language not supported for voice recognition. Switching to English.`;
          break;
        case 'service-not-allowed':
          errorMessage = "Speech recognition service not allowed. Please check browser permissions.";
          break;
        case 'bad-grammar':
          errorMessage = "Speech recognition grammar error. Please try again.";
          break;
        default:
          errorMessage = `Speech recognition error: ${event.error}. Please try again.`;
      }
      
      toast.error(errorMessage);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      setIsListening(false);
      toast.error("Failed to start voice recognition. Please ensure microphone permissions are granted and try again.");
    }
  };

  const stopVoiceRecognition = () => {
    setIsListening(false);
  };

  const getVoiceLanguageCode = (langCode) => {
    const langMap = {
      'eng': 'en-US',
      'spa': 'es-ES', 
      'fra': 'fr-FR',
      'deu': 'de-DE',
      'heb': 'he-IL',
      'ara': 'ar-SA',
      'ita': 'it-IT',
      'por': 'pt-PT',
      'rus': 'ru-RU',
      'chi': 'zh-CN',
      'jpn': 'ja-JP',
      'kor': 'ko-KR',
      'hin': 'hi-IN',
      'tur': 'tr-TR',
      'pol': 'pl-PL',
      'nld': 'nl-NL',
      'swe': 'sv-SE',
      'nor': 'no-NO',
      'dan': 'da-DK',
      'fin': 'fi-FI',
      'hun': 'hu-HU',
      'ces': 'cs-CZ',
      'ron': 'ro-RO',
      'ell': 'el-GR',
      'tha': 'th-TH',
      'vie': 'vi-VN',
      'ind': 'id-ID',
      'auto': 'en-US'
    };
    return langMap[langCode] || 'en-US';
  };

  const downloadFile = async (content, filename, type = 'text/plain') => {
    try {
      // Detect browser type for better error handling
      const isBrave = navigator.brave && await navigator.brave.isBrave();
      const isChrome = /Chrome/.test(navigator.userAgent) && !/Edg/.test(navigator.userAgent);
      const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
      
      // First try using the backend download endpoint for better reliability
      try {
        const response = await axios.post(`${BACKEND_URL}/api/documents/download`, {
          content: content,
          filename: filename
        }, {
          responseType: 'blob'
        });

        // Create download link from blob response
        const blob = new Blob([response.data], { type: type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        
        // For better browser compatibility
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Trigger download
        link.click();
        
        // For Brave browser, detect if download actually started
        if (isBrave) {
          // Wait a moment to see if download started
          setTimeout(async () => {
            try {
              // Check if download was blocked
              const downloadPermission = await navigator.permissions.query({name: 'downloads'}).catch(() => null);
              if (downloadPermission && downloadPermission.state === 'denied') {
                throw new Error('Downloads blocked by browser');
              }
            } catch (permError) {
              // If permissions check fails, provide guidance anyway
              toast.error(
                `🚫 Download may be blocked. Please:\n1. Click the download icon in Brave's address bar\n2. Or go to Settings → Privacy and security → Site and Shields Settings → Downloads → Allow`,
                { duration: 8000 }
              );
            }
          }, 1000);
        }
        
        // Cleanup
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }, 100);
        
        // Success message with browser-specific guidance
        if (isBrave) {
          toast.success(`📁 Download initiated! If not visible, check Brave's download icon in the address bar.`, { duration: 5000 });
        } else {
          toast.success(`📁 File "${filename}" downloaded successfully!`);
        }
        return;
        
      } catch (backendError) {
        console.warn('Backend download failed, trying client-side:', backendError);
      }
      
      // Fallback to client-side download
      const blob = new Blob([content], { type: type });
      
      // Verify blob was created successfully
      if (blob.size === 0) {
        throw new Error("Empty file content - nothing to download");
      }
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      // Better browser compatibility
      link.style.display = 'none';
      document.body.appendChild(link);
      
      // For Brave and strict browsers - check permissions first
      if (navigator.permissions) {
        try {
          const permission = await navigator.permissions.query({name: 'downloads'});
          if (permission.state === 'denied') {
            const settingsUrl = isBrave 
              ? 'brave://settings/content/downloads'
              : isChrome 
                ? 'chrome://settings/content/downloads'
                : isSafari
                  ? 'Browser Preferences → Websites → Downloads'
                  : 'browser download settings';
            
            toast.error(
              `📥 Downloads blocked! To enable:\n1. Go to ${settingsUrl}\n2. Allow downloads for this site\n3. Try downloading again`,
              { duration: 10000 }
            );
            return;
          }
        } catch (permError) {
          // Permissions API not supported, continue with download
          console.log('Download permissions check not supported:', permError);
        }
      }
      
      // Trigger download
      link.click();
      
      // Browser-specific success handling
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        // Provide appropriate feedback based on browser
        if (isBrave) {
          toast.success(
            `📁 Download started! If not visible:\n• Check the download icon in address bar\n• Or press Ctrl+Shift+J to open downloads`,
            { duration: 7000 }
          );
        } else if (isSafari) {
          toast.success(`📁 File saved to Downloads folder. Check Safari's download button if needed.`);
        } else {
          toast.success(`📁 File "${filename}" download completed!`);
        }
      }, 100);
      
    } catch (error) {
      console.error('Download failed:', error);
      
      // Browser-specific error guidance
      const isBrave = navigator.brave && await navigator.brave.isBrave();
      const isChrome = /Chrome/.test(navigator.userAgent) && !/Edg/.test(navigator.userAgent);
      
      let errorMessage = `❌ Download failed: ${error.message}`;
      let guidance = "";
      
      if (isBrave) {
        guidance = "\n\n🔧 Brave Browser Help:\n1. Click the shield icon in address bar\n2. Turn off 'Block downloads'\n3. Or go to brave://settings/content/downloads";
      } else if (isChrome) {
        guidance = "\n\n🔧 Chrome Help:\n1. Check if downloads are blocked (address bar icon)\n2. Or go to chrome://settings/content/downloads";
      }
      
      toast.error(errorMessage + guidance, { duration: 10000 });
    }
  };

  const createMeeting = async () => {
    try {
      setIsLoading(true);
      
      // Create meeting in backend first - let backend generate the ID
      const response = await axios.post(`${BACKEND_URL}/api/meetings`, {
        name: "Translation Meeting",
        participants: [currentUser?.name || "demo-user"]
      });
      
      if (response.data) {
        const meetingId = response.data.id;
        const meetingLink = `${window.location.origin}/meeting/${meetingId}`;
        
        const newMeeting = {
          id: meetingId,
          name: response.data.name,
          participants: response.data.participants,
          createdAt: new Date(),
          status: "active",
          link: meetingLink,
          files: []
        };
        
        setMeetings(prev => [...prev, newMeeting]);
        
        // Copy meeting link to clipboard automatically
        await copyToClipboard(meetingLink);
        
        // Switch to collaborate tab to show the meeting
        setActiveTab("collaborate");
        
        toast.success(`🎥 Meeting created! Link copied to clipboard.`);
        
      }
      
    } catch (error) {
      console.error('Failed to create meeting:', error);
      // Fallback to client-side meeting creation
      const meetingId = `meeting-${Date.now()}`;
      const meetingLink = `${window.location.origin}/meeting/${meetingId}`;
      
      const newMeeting = {
        id: meetingId,
        name: "Translation Meeting",
        participants: [currentUser?.name || "demo-user"],
        createdAt: new Date(),
        status: "active",
        link: meetingLink,
        files: []
      };
      
      setMeetings(prev => [...prev, newMeeting]);
      setActiveTab("collaborate");
      
      // Copy link and notify user
      await copyToClipboard(meetingLink);
      toast.success(`🎥 Meeting created! Share this link: ${meetingLink}`);
    } finally {
      setIsLoading(false);
    }
  };

  const shareMeetingLink = async (meeting) => {
    try {
      await copyToClipboard(meeting.link);
      toast.success(`🔗 Meeting link copied! Share: ${meeting.link}`);
    } catch (error) {
      toast.error("Failed to copy meeting link");
    }
  };

  const shareFileInMeeting = async (meetingId, file) => {
    try {
      // Add file to meeting's shared files
      setMeetings(prev => prev.map(meeting => 
        meeting.id === meetingId 
          ? { ...meeting, files: [...(meeting.files || []), file] }
          : meeting
      ));
      
      toast.success(`📎 File "${file.name}" shared with meeting participants`);
    } catch (error) {
      console.error('Failed to share file:', error);
      toast.error("Failed to share file in meeting");
    }
  };

  const createTeam = async (teamName, teamDescription = "") => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/teams`, {
        name: teamName,
        description: teamDescription
      });
      
      if (response.data) {
        setTeams(prev => [...prev, response.data]);
        setCurrentTeam(response.data);
        toast.success(`🏢 Team "${teamName}" created! Invite code: ${response.data.invite_code}`);
        
        // Copy invite code to clipboard
        await copyToClipboard(response.data.invite_code);
        setShowTeamCreator(false);
      }
    } catch (error) {
      console.error('Failed to create team:', error);
      toast.error("Failed to create team");
    }
  };

  // Load user teams
  const loadUserTeams = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/teams`, {
        params: { user_id: currentUser?.id || "demo-user" }
      });
      if (response.data) {
        setTeams(response.data);
      }
    } catch (error) {
      console.error('Failed to load teams:', error);
    }
  };

  // Upload file to team
  const uploadTeamFile = async (teamId, file, description = "", tags = "") => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', description);
      formData.append('tags', tags);
      formData.append('user_id', currentUser?.id || "demo-user");

      const response = await axios.post(`${BACKEND_URL}/api/teams/${teamId}/files/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data) {
        toast.success(`✅ File "${file.name}" uploaded to team successfully!`);
        // Reload team files
        await loadTeamFiles(teamId);
        setShowFileUpload(false);
      }
    } catch (error) {
      console.error('Failed to upload team file:', error);
      toast.error("Failed to upload file to team");
    }
  };

  // Load team files
  const loadTeamFiles = async (teamId) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/teams/${teamId}/files`, {
        params: { user_id: currentUser?.id || "demo-user" }
      });
      if (response.data) {
        setTeamFiles(response.data.files);
      }
    } catch (error) {
      console.error('Failed to load team files:', error);
      toast.error("Failed to load team files");
    }
  };

  // Download team file
  const downloadTeamFile = async (teamId, fileId, filename) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/teams/${teamId}/files/${fileId}/download`, {
        params: { user_id: currentUser?.id || "demo-user" },
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`📁 Downloaded: ${filename}`);
    } catch (error) {
      console.error('Failed to download team file:', error);
      toast.error("Failed to download file");
    }
  };

  // Delete team file
  const deleteTeamFile = async (teamId, fileId, filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      await axios.delete(`${BACKEND_URL}/api/teams/${teamId}/files/${fileId}`, {
        params: { user_id: currentUser?.id || "demo-user" }
      });

      toast.success(`🗑️ Deleted: ${filename}`);
      // Reload team files
      await loadTeamFiles(teamId);
    } catch (error) {
      console.error('Failed to delete team file:', error);
      toast.error("Failed to delete file");
    }
  };

  // Initialize WebSocket connection
  const initializeWebSocket = () => {
    if (websocket) {
      websocket.close();
    }

    const userId = currentUser?.id || `user-${Date.now()}`;
    const wsUrl = BACKEND_URL.replace('http', 'ws') + `/ws/${userId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWebsocket(ws);
    };

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      await handleWebSocketMessage(data);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWebsocket(null);
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (currentUser) {
          initializeWebSocket();
        }
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  // Handle incoming WebSocket messages
  const handleWebSocketMessage = async (data) => {
    switch (data.type) {
      case 'user_joined':
        console.log('User joined:', data.user_id);
        setConnectedUsers(prev => [...prev.filter(u => u !== data.user_id), data.user_id]);
        break;

      case 'user_left':
        console.log('User left:', data.user_id);
        setConnectedUsers(prev => prev.filter(u => u !== data.user_id));
        break;

      case 'existing_participants':
        console.log('Existing participants:', data.participants);
        setConnectedUsers(data.participants);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const joinTeam = async (inviteCode) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/teams/join`, {
        invite_code: inviteCode,
        user_id: currentUser?.id || "demo-user"
      });
      
      if (response.data) {
        setTeams(prev => {
          const existing = prev.find(t => t.id === response.data.id);
          if (!existing) {
            return [...prev, response.data];
          }
          return prev;
        });
        setCurrentTeam(response.data);
        toast.success(`🎉 Joined team: ${response.data.name}`);
      }
    } catch (error) {
      console.error('Failed to join team:', error);
      toast.error("Invalid invite code or team not found");
    }
  };

  // Simplified video meeting functionality - WebRTC moved to future development
  const joinMeeting = (meetingId) => {
    // Show "Coming soon" message instead of WebRTC implementation
    toast.info("🚀 Video calling coming soon! We're working on an amazing video experience for you.", {
      duration: 4000,
      icon: "🎥"
    });
  };

  const leaveMeeting = () => {
    // Stop local stream
    if (localStream) {
      localStream.getTracks().forEach(track => {
        track.stop();
      });
      setLocalStream(null);
    }
    
    // Close all peer connections
    peerConnections.forEach((peerConnection, userId) => {
      peerConnection.close();
    });
    setPeerConnections(new Map());
    
    // Clear remote streams
    setRemoteStreams(new Map());
    setConnectedUsers([]);
    
    // Notify other users via WebSocket
    if (websocket && currentMeetingId) {
      websocket.send(JSON.stringify({
        type: 'leave_meeting',
        meeting_id: currentMeetingId
      }));
    }
    
    setCurrentMeetingId(null);
    toast.success("📞 Left the meeting");
  };

  const shareFile = (file) => {
    const sharedFile = {
      id: `file-${Date.now()}`,
      name: file.filename,
      sharedBy: currentUser.name,
      sharedAt: new Date(),
      type: file.document_type
    };
    setSharedFiles(prev => [...prev, sharedFile]);
    toast.success("File shared with team");
  };

  const clearNotifications = () => {
    setNotifications([]);
    toast.success("Notifications cleared");
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)] transition-colors duration-300">
      <Toaster position="top-right" />
      
      {/* Login Dialog */}
      {showLogin && (
        <Dialog open={showLogin} onOpenChange={() => {}}>
          <DialogContent className="card-elevated sm:max-w-md">
            <DialogHeader>
              <div className="w-16 h-16 bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <Globe className="h-8 w-8 text-white" />
              </div>
              <DialogTitle className="text-display mb-2 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-accent)] bg-clip-text text-transparent text-center">
                Welcome to Comprende
              </DialogTitle>
              <p className="text-body-large text-center">
                AI-powered collaboration platform for seamless team communication
              </p>
            </DialogHeader>
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const userData = {
                  name: formData.get('name'),
                  email: formData.get('email'),
                  avatar: formData.get('avatar') || null
                };
                if (userData.name && userData.email) {
                  loginUser(userData);
                }
              }}
              className="space-y-4"
            >
              <div>
                <label className="text-body-small font-medium block mb-2">Full Name</label>
                <Input name="name" type="text" placeholder="Enter your full name" required className="focus-ring" />
              </div>
              <div>
                <label className="text-body-small font-medium block mb-2">Email Address</label>
                <Input name="email" type="email" placeholder="Enter your email" required className="focus-ring" />
              </div>
              <div>
                <label className="text-body-small font-medium block mb-2">Avatar</label>
                <div className="space-y-2">
                  <Input 
                    type="file" 
                    accept="image/*" 
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        if (file.size > 1024 * 1024) {
                          toast.error("Avatar image must be smaller than 1MB");
                          e.target.value = '';
                          return;
                        }
                        const reader = new FileReader();
                        reader.onload = (event) => {
                          const preview = document.getElementById('avatar-preview');
                          if (preview) {
                            preview.src = event.target.result;
                            preview.style.display = 'block';
                          }
                          // Store the data URL in a hidden input
                          const hiddenInput = document.getElementById('avatar-data');
                          if (hiddenInput) {
                            hiddenInput.value = event.target.result;
                          }
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                    className="mb-2 focus-ring"
                  />
                  <input type="hidden" name="avatar" id="avatar-data" />
                  <img 
                    id="avatar-preview" 
                    style={{display: 'none'}} 
                    className="w-10 h-10 rounded-full object-cover border border-[var(--color-border)]" 
                    alt="Avatar preview"
                  />
                  <p className="text-caption">
                    Upload an image (max 1MB) or we'll use your Gravatar
                  </p>
                </div>
              </div>
              <Button type="submit" className="w-full btn-primary">
                <Zap className="h-4 w-4 mr-2" />
                Get Started
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      )}
      
      {/* Main App Content - Only show when logged in */}
      {!showLogin && currentUser && (
        <>
      {/* Enhanced Header with Modern Design */}
      <header className="sticky top-0 z-50 bg-[var(--color-surface-elevated)]/95 backdrop-blur-md border-b border-[var(--color-border)]">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Brand */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] rounded-xl flex items-center justify-center shadow-lg">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-heading-3 font-bold bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-accent)] bg-clip-text text-transparent">
                  Comprende
                </h1>
                <p className="text-caption text-[var(--color-text-tertiary)]">AI-Powered Collaboration</p>
              </div>
            </div>

            {/* Navigation and User Actions */}
            <div className="flex items-center space-x-4">
              {/* System Health Status */}
              {healthStatus?.status && (
                <div className={`status-indicator ${healthStatus.status === 'healthy' ? 'status-healthy' : 'status-error'}`}>
                  <div className={`status-dot ${healthStatus.status === 'healthy' ? 'healthy' : 'error'}`}></div>
                  <span className="text-caption">System {healthStatus.status}</span>
                </div>
              )}

              {/* Notifications */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="relative btn-secondary">
                    <Bell className="h-4 w-4" />
                    {notifications.length > 0 && (
                      <span className="absolute -top-1 -right-1 bg-[var(--color-danger)] text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                        {notifications.length}
                      </span>
                    )}
                  </Button>
                </DialogTrigger>
                <DialogContent className="notifications-dialog">
                  <DialogHeader className="mb-4">
                    <DialogTitle className="text-heading-3">Notifications</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-3">
                    {notifications.length > 0 ? (
                      <>
                        {notifications.map(notification => (
                          <div key={notification.id} className="file-card">
                            <p className="text-body-small">{notification.message}</p>
                            <p className="text-caption mt-1">{notification.created_at}</p>
                          </div>
                        ))}
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setNotifications([])}
                          className="w-full dialog-button-secondary"
                        >
                          Clear All
                        </Button>
                      </>
                    ) : (
                      <div className="empty-state">
                        <div className="empty-state-icon">
                          <Bell className="h-6 w-6" />
                        </div>
                        <p className="text-body-small">No notifications</p>
                      </div>
                    )}
                  </div>
                </DialogContent>
              </Dialog>

              {/* Settings */}
              <Dialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="btn-secondary">
                    <Settings className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="settings-dialog">
                  <DialogHeader className="mb-6">
                    <DialogTitle className="text-heading-3 mb-2">Settings</DialogTitle>
                    <p className="text-body text-[var(--color-text-secondary)]">
                      Customize your translation and collaboration preferences
                    </p>
                  </DialogHeader>
                  <div className="space-y-6">
                    <div className="settings-section">
                      <label className="settings-label">Default Source Language</label>
                      <div className="settings-select">
                        <Select 
                          value={settings.defaultSourceLang} 
                          onValueChange={(value) => {
                            try {
                              setSettings(prev => ({...prev, defaultSourceLang: value}));
                              setSourceLang(value);
                              toast.success(`Source language set to ${value === 'auto' ? 'Auto-detect' : LANGUAGES[value] || value}`);
                            } catch (error) {
                              console.error('Error updating source language:', error);
                              toast.error('Failed to update source language');
                            }
                          }}
                        >
                          <SelectTrigger className="focus-ring">
                            <SelectValue placeholder="Select source language" />
                          </SelectTrigger>
                          <SelectContent className="max-h-60 overflow-y-auto">
                            <SelectItem value="auto">🌐 Auto-detect</SelectItem>
                            {Object.entries(LANGUAGES).map(([code, name]) => (
                              <SelectItem key={code} value={code}>
                                {name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="settings-section">
                      <label className="settings-label">Default Target Language</label>
                      <div className="settings-select">
                        <Select 
                          value={settings.defaultTargetLang}
                          onValueChange={(value) => {
                            try {
                              setSettings(prev => ({...prev, defaultTargetLang: value}));
                              setTargetLang(value);
                              toast.success(`Target language set to ${LANGUAGES[value] || value}`);
                            } catch (error) {
                              console.error('Error updating target language:', error);
                              toast.error('Failed to update target language');
                            }
                          }}
                        >
                          <SelectTrigger className="focus-ring">
                            <SelectValue placeholder="Select target language" />
                          </SelectTrigger>
                          <SelectContent className="max-h-60 overflow-y-auto">
                            {Object.entries(LANGUAGES).map(([code, name]) => (
                              <SelectItem key={code} value={code}>
                                {name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="settings-section">
                      <label className="settings-label">Voice & Audio Settings</label>
                      <div className="voice-settings">
                        <div className="voice-setting-item">
                          <label 
                            className="voice-setting-label"
                            onClick={(e) => {
                              e.preventDefault();
                              const newValue = !settings.voiceInputEnabled;
                              setSettings(prev => ({...prev, voiceInputEnabled: newValue}));
                              toast.success(`Voice input ${newValue ? 'enabled' : 'disabled'}`);
                            }}
                          >
                            <input 
                              type="checkbox" 
                              checked={settings.voiceInputEnabled}
                              onChange={() => {}} // Controlled by label click
                              className="sr-only"
                            />
                            <div className={`voice-setting-checkbox ${settings.voiceInputEnabled ? 'checked' : ''}`}></div>
                            <div className="voice-setting-content">
                              <span className="voice-setting-title">Enable Voice Input</span>
                              <p className="voice-setting-description">
                                Allow microphone access for voice translations
                              </p>
                            </div>
                          </label>
                        </div>

                        <div className="voice-setting-item">
                          <label 
                            className="voice-setting-label"
                            onClick={(e) => {
                              e.preventDefault();
                              const newValue = !settings.voiceOutputEnabled;
                              setSettings(prev => ({...prev, voiceOutputEnabled: newValue}));
                              toast.success(`Voice output ${newValue ? 'enabled' : 'disabled'}`);
                            }}
                          >
                            <input 
                              type="checkbox" 
                              checked={settings.voiceOutputEnabled}
                              onChange={() => {}} // Controlled by label click
                              className="sr-only"
                            />
                            <div className={`voice-setting-checkbox ${settings.voiceOutputEnabled ? 'checked' : ''}`}></div>
                            <div className="voice-setting-content">
                              <span className="voice-setting-title">Enable Voice Output</span>
                              <p className="voice-setting-description">
                                Play translated text using text-to-speech
                              </p>
                            </div>
                          </label>
                        </div>

                        <div className="voice-setting-item">
                          <label 
                            className="voice-setting-label"
                            onClick={(e) => {
                              e.preventDefault();
                              const newValue = !settings.autoTranslateVoice;
                              setSettings(prev => ({...prev, autoTranslateVoice: newValue}));
                              toast.success(`Auto-translate voice ${newValue ? 'enabled' : 'disabled'}`);
                            }}
                          >
                            <input 
                              type="checkbox" 
                              checked={settings.autoTranslateVoice}
                              onChange={() => {}} // Controlled by label click
                              className="sr-only"
                            />
                            <div className={`voice-setting-checkbox ${settings.autoTranslateVoice ? 'checked' : ''}`}></div>
                            <div className="voice-setting-content">
                              <span className="voice-setting-title">Auto-translate Voice Input</span>
                              <p className="voice-setting-description">
                                Automatically translate speech when detected
                              </p>
                            </div>
                          </label>
                        </div>
                      </div>
                    </div>

                    <div className="settings-footer">
                      <button
                        type="button"
                        onClick={() => {
                          // Reset to defaults
                          const defaultSettings = {
                            defaultSourceLang: 'auto',
                            defaultTargetLang: 'eng',
                            voiceInputEnabled: true,
                            voiceOutputEnabled: true,
                            autoTranslateVoice: false
                          };
                          setSettings(defaultSettings);
                          toast.success('Settings reset to defaults');
                        }}
                        className="settings-button-reset"
                      >
                        Reset to Defaults
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setIsSettingsOpen(false);
                          toast.success('Settings saved successfully');
                        }}
                        className="settings-button-save"
                      >
                        Save Settings
                      </button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              {/* User Profile */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="flex items-center space-x-2 btn-secondary">
                    {currentUser.avatar && currentUser.avatar.startsWith('data:') ? (
                      <img 
                        src={currentUser.avatar} 
                        alt="User avatar" 
                        className="w-6 h-6 rounded-full object-cover"
                      />
                    ) : currentUser.avatar && currentUser.avatar.startsWith('http') ? (
                      <img 
                        src={currentUser.avatar} 
                        alt="User avatar" 
                        className="w-6 h-6 rounded-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'inline';
                        }}
                      />
                    ) : (
                      <User className="h-5 w-5" />
                    )}
                    <span className="text-lg" style={{display: 'none'}}>👤</span>
                    <span className="hidden sm:inline text-body-small">{currentUser.name}</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="user-profile-dialog">
                  <DialogHeader>
                    <DialogTitle className="text-heading-3">User Profile</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      {currentUser.avatar && currentUser.avatar.startsWith('data:') ? (
                        <img 
                          src={currentUser.avatar} 
                          alt="User avatar" 
                          className="w-12 h-12 rounded-full object-cover border border-[var(--color-border)]"
                        />
                      ) : currentUser.avatar && currentUser.avatar.startsWith('http') ? (
                        <img 
                          src={currentUser.avatar} 
                          alt="User avatar" 
                          className="w-12 h-12 rounded-full object-cover border border-[var(--color-border)]"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'inline';
                          }}
                        />
                      ) : (
                        <div className="w-12 h-12 bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] rounded-full flex items-center justify-center">
                          <User className="h-6 w-6 text-white" />
                        </div>
                      )}
                      <span className="text-3xl" style={{display: 'none'}}>👤</span>
                      <div>
                        <p className="text-body font-medium">{currentUser.name}</p>
                        <p className="text-caption text-[var(--color-text-tertiary)]">{currentUser.email}</p>
                      </div>
                    </div>
                    <div>
                      <label className="text-body-small font-medium">Update Avatar</label>
                      <Input 
                        type="file" 
                        accept="image/*" 
                        onChange={handleAvatarUpload}
                        className="mt-1 input-field"
                      />
                      <p className="text-caption text-[var(--color-text-tertiary)] mt-1">
                        Upload a new avatar image (max 1MB)
                      </p>
                    </div>
                    <div className="pt-4 border-t border-[var(--color-border)]">
                      <Button onClick={logoutUser} variant="outline" className="w-full btn-secondary">
                        Logout
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="translate" className="flex items-center space-x-2">
              <Languages className="h-4 w-4" />
              <span className="hidden sm:inline">Translate</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Documents</span>
            </TabsTrigger>
            <TabsTrigger value="collaborate" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Collaborate</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span className="hidden sm:inline">Security</span>
            </TabsTrigger>
          </TabsList>

          {/* Translation Tab */}
          <TabsContent value="translate" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-slate-800">
                      <Zap className="h-5 w-5 text-blue-600" />
                      <span>Real-time Translation</span>
                    </CardTitle>
                    <CardDescription>
                      Translate text between {Object.keys(LANGUAGES).length}+ languages with AI-powered context awareness
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Language Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">From</label>
                        <Select value={sourceLang} onValueChange={setSourceLang}>
                          <SelectTrigger className="bg-white border-gray-300 text-gray-900 shadow-sm hover:border-blue-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
                            <SelectValue placeholder="Source Language" className="text-gray-900" />
                          </SelectTrigger>
                          <SelectContent className="max-h-60 overflow-y-auto bg-white border-gray-300 shadow-xl z-50">
                            <SelectItem 
                              value="auto" 
                              className="font-medium text-gray-900 hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200 focus:text-blue-900 cursor-pointer py-2"
                            >
                              Auto-detect
                            </SelectItem>
                            {Object.entries(LANGUAGES)
                              .sort(([,a], [,b]) => a.localeCompare(b))
                              .map(([code, name]) => (
                              <SelectItem 
                                key={code} 
                                value={code}
                                className="text-gray-900 hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200 focus:text-blue-900 cursor-pointer py-2"
                              >
                                {name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {detectedLanguage && sourceLang === "auto" && (
                          <p className="text-xs text-blue-600 mt-1">
                            Detected: {LANGUAGES[detectedLanguage] || detectedLanguage}
                          </p>
                        )}
                      </div>

                      <Button variant="ghost" className="flex items-center justify-center mt-6">
                        <Languages className="h-4 w-4" />
                      </Button>

                      <div>
                        <label className="text-sm font-medium mb-2 block">To</label>
                        <Select value={targetLang} onValueChange={setTargetLang}>
                          <SelectTrigger className="bg-white border-gray-300 text-gray-900 shadow-sm hover:border-blue-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
                            <SelectValue placeholder="Target Language" className="text-gray-900" />
                          </SelectTrigger>
                          <SelectContent className="max-h-60 overflow-y-auto bg-white border-gray-300 shadow-xl z-50">
                            {Object.entries(LANGUAGES)
                              .sort(([,a], [,b]) => a.localeCompare(b))
                              .map(([code, name]) => (
                              <SelectItem 
                                key={code} 
                                value={code}
                                className="text-gray-900 hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200 focus:text-blue-900 cursor-pointer py-2"
                              >
                                {name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Context Selection */}
                    <div className="grid grid-cols-2 gap-4">
                      <Select value={context} onValueChange={setContext}>
                        <SelectTrigger>
                          <SelectValue placeholder="Context" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="general">General</SelectItem>
                          <SelectItem value="formal">Formal</SelectItem>
                          <SelectItem value="casual">Casual</SelectItem>
                          <SelectItem value="technical">Technical</SelectItem>
                        </SelectContent>
                      </Select>

                      <Select value={industry} onValueChange={setIndustry}>
                        <SelectTrigger>
                          <SelectValue placeholder="Industry" />
                        </SelectTrigger>
                        <SelectContent className="max-h-60 overflow-y-auto">
                          {Object.entries(INDUSTRIES).map(([code, name]) => (
                            <SelectItem key={code} value={code}>{name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Input Area */}
                    <div className="space-y-4">
                      <div className="relative">
                        <Textarea
                          placeholder="Enter text to translate..."
                          value={sourceText}
                          onChange={(e) => setSourceText(e.target.value)}
                          className="min-h-32 resize-none pr-16 pb-12"
                          dir={sourceLang === 'heb' || sourceLang === 'ara' ? 'rtl' : 'ltr'}
                        />
                        <div className="absolute bottom-3 right-3 flex items-center space-x-2">
                          <Button
                            variant={isListening ? "destructive" : "secondary"}
                            size="sm"
                            className={`h-8 w-8 p-0 shadow-sm ${
                              isListening 
                                ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse border-red-300' 
                                : 'bg-blue-500 hover:bg-blue-600 text-white border-blue-300'
                            }`}
                            onClick={toggleVoiceInput}
                            title={isListening ? "Stop voice input" : "Start voice input"}
                          >
                            {isListening ? (
                              <MicOff className="h-4 w-4" />
                            ) : (
                              <Mic className="h-4 w-4" />
                            )}
                          </Button>
                          {settings.voiceInputEnabled && (
                            <span className="text-xs text-gray-500 hidden sm:inline">
                              {isListening ? "Listening..." : "Voice"}
                            </span>
                          )}
                        </div>
                      </div>

                      <Button 
                        onClick={handleTranslate} 
                        disabled={isLoading || !sourceText.trim()}
                        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium shadow-lg disabled:opacity-50 disabled:cursor-not-allowed border-0"
                      >
                        {isLoading ? (
                          <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span className="text-white">Translating...</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2">
                            <Languages className="h-4 w-4 text-white" />
                            <span className="text-white font-medium">Translate</span>
                          </div>
                        )}
                      </Button>
                    </div>

                    {/* Output Area */}
                    {translatedText && (
                      <div className="space-y-4">
                        <Separator />
                        <div className="relative">
                          <Textarea
                            value={translatedText}
                            readOnly
                            className="min-h-32 bg-slate-50 border-slate-200"
                            dir={targetLang === 'heb' || targetLang === 'ara' ? 'rtl' : 'ltr'}
                          />
                          <div className="absolute bottom-2 right-2 flex space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(translatedText)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => speakText(translatedText, targetLang)}
                              disabled={isSpeaking}
                            >
                              {isSpeaking ? <Pause className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => downloadFile(translatedText, 'translation.txt')}
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Quick Actions */}
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-slate-800">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button variant="outline" className="w-full justify-start" onClick={() => setActiveTab("documents")}>
                      <Camera className="h-4 w-4 mr-2" />
                      Scan Document
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={toggleVoiceInput}>
                      <Mic className="h-4 w-4 mr-2" />
                      Voice Translation
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={createMeeting}>
                      <Users className="h-4 w-4 mr-2" />
                      Start Meeting
                    </Button>
                  </CardContent>
                </Card>

                {/* Recent Translations */}
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-slate-800">Recent Translations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {translationHistory.length > 0 ? (
                      <div className="space-y-3">
                        {translationHistory.slice(0, 5).map((translation, index) => (
                          <div key={index} className="p-3 bg-slate-50 rounded-lg text-sm">
                            <div className="flex items-center justify-between mb-1">
                              <Badge variant="secondary" className="text-xs">
                                {LANGUAGES[translation.source_language]} → {LANGUAGES[translation.target_language]}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {new Date(translation.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-gray-700 truncate">
                              {translation.original_text?.slice(0, 50)}...
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No recent translations</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-slate-800">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <span>Document Processing</span>
                </CardTitle>
                <CardDescription>
                  Scan, extract text, and translate documents in multiple formats
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* File Upload */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-gray-700">Upload Document</p>
                    <p className="text-sm text-gray-500">
                      Supports PDF, Images (JPG, PNG), Text files up to 10MB
                    </p>
                    <Input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png,.txt,.docx,.tiff,.bmp"
                      onChange={(e) => setFile(e.target.files[0])}
                      className="max-w-xs mx-auto"
                    />
                  </div>
                  
                  {/* Mobile Scan Button */}
                  <div className="mt-4 sm:hidden">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => {
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.accept = 'image/*';
                        input.capture = 'environment';
                        input.onchange = (e) => setFile(e.target.files[0]);
                        input.click();
                      }}
                    >
                      <Camera className="h-4 w-4 mr-2" />
                      Scan with Camera
                    </Button>
                  </div>
                </div>

                {file && (
                  <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <div>
                        <span className="font-medium text-blue-900">{file.name}</span>
                        <p className="text-sm text-blue-600">
                          Size: {(file.size / 1024).toFixed(1)} KB • Type: {file.type || 'Unknown'}
                        </p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button 
                        onClick={handleDocumentUpload} 
                        disabled={isLoading}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        {isLoading ? "Processing..." : "Process Document"}
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => setFile(null)}
                        disabled={isLoading}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                )}

                {/* Uploaded Files */}
                {uploadedFiles.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-800">Processed Documents</h3>
                    {uploadedFiles.map((doc, index) => (
                      <Card key={index}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">{doc.filename}</h4>
                            <div className="flex space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => shareFile(doc)}
                              >
                                <Send className="h-4 w-4 mr-1" />
                                Share
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => downloadFile(doc.extracted_text, `${doc.filename}_extracted.txt`)}
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </Button>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                            <div>
                              <span className="font-medium">Language:</span>
                              <Badge className="ml-2">{LANGUAGES[doc.detected_language]}</Badge>
                            </div>
                            <div>
                              <span className="font-medium">Confidence:</span>
                              <span className="ml-2">{(doc.confidence * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                          <div className="p-3 bg-gray-50 rounded border max-h-32 overflow-y-auto">
                            <p className="text-sm">{doc.extracted_text}</p>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {/* Document Result */}
                {documentResult && (
                  <Card className="mt-6">
                    <CardHeader>
                      <CardTitle className="text-lg">Processing Results</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Language Detected:</span>
                          <Badge className="ml-2">{LANGUAGES[documentResult.detected_language]}</Badge>
                        </div>
                        <div>
                          <span className="font-medium">Confidence:</span>
                          <span className="ml-2">{(documentResult.confidence * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2 flex items-center space-x-2">
                          <span>Extracted Text:</span>
                          <Badge variant="outline" className="text-xs">
                            {LANGUAGES[documentResult.detected_language]} • {(documentResult.confidence * 100).toFixed(1)}% confidence
                          </Badge>
                        </h4>
                        <div className="p-3 bg-gray-50 rounded border max-h-40 overflow-y-auto">
                          <p className="text-sm whitespace-pre-wrap">{documentResult.extracted_text}</p>
                        </div>
                      </div>

                      {documentResult.translated_text && (
                        <div>
                          <h4 className="font-medium mb-2 flex items-center space-x-2">
                            <span>Translated Text:</span>
                            <Badge variant="outline" className="text-xs bg-blue-50">
                              {LANGUAGES[documentResult.detected_language]} → {LANGUAGES[targetLang]}
                            </Badge>
                          </h4>
                          <div className="p-3 bg-blue-50 rounded border max-h-40 overflow-y-auto">
                            <p className="text-sm whitespace-pre-wrap">{documentResult.translated_text}</p>
                          </div>
                        </div>
                      )}

                      <div className="flex flex-wrap gap-2">
                        <Button variant="outline" size="sm" onClick={() => copyToClipboard(documentResult.extracted_text)}>
                          <Copy className="h-4 w-4 mr-1" />
                          Copy Original
                        </Button>
                        {documentResult.translated_text && (
                          <Button variant="outline" size="sm" onClick={() => copyToClipboard(documentResult.translated_text)}>
                            <Copy className="h-4 w-4 mr-1" />
                            Copy Translation
                          </Button>
                        )}
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            const originalExt = documentResult.filename.split('.').pop().toLowerCase();
                            const downloadName = `${documentResult.filename}_original.${originalExt}`;
                            if (['pdf', 'xls', 'xlsx'].includes(originalExt)) {
                              downloadFileFormatted(documentResult.extracted_text, downloadName, originalExt);
                            } else {
                              downloadFile(documentResult.extracted_text, downloadName);
                            }
                          }}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download Original ({documentResult.filename.split('.').pop().toUpperCase()})
                        </Button>
                        {documentResult.translated_text && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              const originalExt = documentResult.filename.split('.').pop().toLowerCase();
                              const downloadName = `${documentResult.filename}_translated.${originalExt}`;
                              if (['pdf', 'xls', 'xlsx'].includes(originalExt)) {
                                downloadFileFormatted(documentResult.translated_text, downloadName, originalExt);
                              } else {
                                downloadFile(documentResult.translated_text, downloadName);
                              }
                            }}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download Translation ({documentResult.filename.split('.').pop().toUpperCase()})
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Collaborate Tab */}
          <TabsContent value="collaborate" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Teams Management Area */}
              <div className="lg:col-span-2 space-y-6">
                
                {/* Teams Overview */}
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-slate-800">
                      <Users className="h-5 w-5 text-blue-600" />
                      <span>My Teams</span>
                    </CardTitle>
                    <CardDescription>
                      Collaborate with your teams and share files securely
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex space-x-4">
                      <Button onClick={() => setShowTeamCreator(true)} className="bg-blue-600 hover:bg-blue-700">
                        <Plus className="h-4 w-4 mr-2" />
                        Create Team
                      </Button>
                      <Button variant="outline" onClick={() => setShowTeamJoiner(true)}>
                        <UserPlus className="h-4 w-4 mr-2" />
                        Join Team
                      </Button>
                    </div>

                    {/* Teams List */}
                    {teams.length > 0 ? (
                      <div className="space-y-3">
                        <h3 className="font-semibold">Your Teams ({teams.length})</h3>
                        {teams.map(team => (
                          <div key={team.id} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex-1">
                                <h4 className="font-medium text-lg">{team.name}</h4>
                                {team.description && (
                                  <p className="text-sm text-gray-600 mt-1">{team.description}</p>
                                )}
                                <div className="flex items-center space-x-4 mt-2">
                                  <span className="text-sm text-gray-500">
                                    👥 {team.members?.length || 0} members
                                  </span>
                                  <span className="text-sm text-gray-500">
                                    📅 Created {new Date(team.created_at).toLocaleDateString()}
                                  </span>
                                  <Badge variant="outline" className="text-xs">
                                    Code: {team.invite_code}
                                  </Badge>
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => copyToClipboard(team.invite_code)}
                                  title="Copy invite code"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                                <Button 
                                  size="sm"
                                  onClick={() => {
                                    setCurrentTeam(team);
                                    setSelectedTeamForFiles(team.id);
                                    loadTeamFiles(team.id);
                                  }}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <FolderOpen className="h-4 w-4 mr-1" />
                                  View Files
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-500">
                        <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <h3 className="font-medium mb-2">No teams yet</h3>
                        <p className="text-sm mb-4">Create a team to start collaborating with others</p>
                        <Button onClick={() => setShowTeamCreator(true)} className="bg-blue-600 hover:bg-blue-700">
                          Create Your First Team
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Team Files Area */}
                {currentTeam && (
                  <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2 text-slate-800">
                        <FolderOpen className="h-5 w-5 text-green-600" />
                        <span>{currentTeam.name} - Files</span>
                      </CardTitle>
                      <CardDescription>
                        Shared files and documents for team collaboration
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex space-x-4">
                        <Button 
                          onClick={() => setShowFileUpload(true)} 
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Upload className="h-4 w-4 mr-2" />
                          Upload File
                        </Button>
                        <Button variant="outline" onClick={() => loadTeamFiles(currentTeam.id)}>
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Refresh
                        </Button>
                      </div>

                      {/* Team Files List */}
                      {teamFiles.length > 0 ? (
                        <div className="space-y-3">
                          <h3 className="font-semibold">Team Files ({teamFiles.length})</h3>
                          {teamFiles.map(file => (
                            <div key={file.id} className="p-3 border rounded-lg hover:bg-gray-50">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2">
                                    <FileText className="h-4 w-4 text-blue-600" />
                                    <span className="font-medium">{file.original_name}</span>
                                    <Badge variant="outline" className="text-xs">
                                      {file.file_type}
                                    </Badge>
                                  </div>
                                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                                    <span>👤 {file.uploaded_by}</span>
                                    <span>📅 {new Date(file.created_at).toLocaleDateString()}</span>
                                    <span>📏 {(file.file_size / 1024).toFixed(1)} KB</span>
                                  </div>
                                  {file.description && (
                                    <p className="text-sm text-gray-600 mt-1">{file.description}</p>
                                  )}
                                  {file.tags && file.tags.length > 0 && (
                                    <div className="flex space-x-1 mt-1">
                                      {file.tags.map(tag => (
                                        <Badge key={tag} variant="secondary" className="text-xs">
                                          {tag}
                                        </Badge>
                                      ))}
                                    </div>
                                  )}
                                </div>
                                <div className="flex space-x-2">
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={() => downloadTeamFile(currentTeam.id, file.id, file.original_name)}
                                    title="Download file"
                                  >
                                    <Download className="h-4 w-4" />
                                  </Button>
                                  {(file.uploaded_by === (currentUser?.id || "demo-user") || 
                                    currentTeam.created_by === (currentUser?.id || "demo-user")) && (
                                    <Button 
                                      size="sm" 
                                      variant="outline"
                                      onClick={() => deleteTeamFile(currentTeam.id, file.id, file.original_name)}
                                      className="text-red-600 hover:text-red-700"
                                      title="Delete file"
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <FileText className="h-10 w-10 mx-auto mb-3 text-gray-300" />
                          <h4 className="font-medium mb-2">No files yet</h4>
                          <p className="text-sm">Upload files to share with your team</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Video Meetings Section with Coming Soon Message */}
                <Card className="card-elevated">
                  <CardHeader>
                    <CardTitle className="text-heading-3 flex items-center space-x-2">
                      <Video className="h-5 w-5 text-[var(--color-primary)]" />
                      <span>Video Meetings</span>
                    </CardTitle>
                    <CardDescription className="text-body">
                      Advanced video collaboration features
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex space-x-4">
                      <Button onClick={createMeeting} className="btn-primary">
                        <Plus className="h-4 w-4 mr-2" />
                        Start Meeting
                      </Button>
                    </div>

                    {/* Active Meetings */}
                    {meetings.length > 0 && (
                      <div className="space-y-3">
                        <h3 className="text-heading-3">Active Meetings</h3>
                        {meetings.map(meeting => (
                          <div key={meeting.id} className="team-card">
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <h4 className="text-body font-medium">{meeting.name}</h4>
                                <p className="text-body-small text-[var(--color-text-tertiary)]">
                                  Meeting ID: {meeting.id}
                                </p>
                                <div className="flex items-center space-x-4 mt-2">
                                  <span className="text-caption">
                                    👥 {meeting.participants?.length || 0} participants
                                  </span>
                                  <span className="text-caption">
                                    📅 {new Date(meeting.createdAt).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <Button 
                                  size="sm" 
                                  onClick={() => joinMeeting(meeting.id)}
                                  disabled={isLoading}
                                  className="btn-primary"
                                >
                                  {isLoading ? (
                                    <span className="flex items-center">
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                                      <span>Connecting...</span>
                                    </span>
                                  ) : (
                                    <>
                                      <Video className="h-4 w-4 mr-1" />
                                      <span>Join Video</span>
                                    </>
                                  )}
                                </Button>
                                <Button 
                                  variant="outline" 
                                  size="sm" 
                                  title="Copy meeting link to share"
                                  onClick={() => shareMeetingLink(meeting)}
                                  className="btn-accent"
                                >
                                  <Share className="h-4 w-4 mr-1" />
                                  <span>Copy Link</span>
                                </Button>
                              </div>
                            </div>
                            
                            {/* Coming Soon Video Interface */}
                            <div className="mt-4 coming-soon">
                              <div className="coming-soon-icon">
                                <Video className="h-6 w-6" />
                              </div>
                              <h4 className="text-heading-3 mb-2">🚀 Video Calling Coming Soon!</h4>
                              <p className="text-body text-[var(--color-text-secondary)]">
                                We're building an amazing video experience with HD quality, screen sharing, 
                                and real-time collaboration features.
                              </p>
                              <div className="flex items-center justify-center space-x-4 mt-4 text-caption text-[var(--color-text-tertiary)]">
                                <span>📹 HD Video</span>
                                <span>🖥️ Screen Share</span>
                                <span>🎙️ Crystal Audio</span>
                                <span>💬 Live Chat</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Team Sidebar */}
              <div className="space-y-6">
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-slate-800">Team Members</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {users.map(user => (
                        <div key={user.id} className="flex items-center space-x-3">
                          <div className="text-2xl">{user.avatar}</div>
                          <div className="flex-1">
                            <p className="font-medium">{user.name}</p>
                            <div className="flex items-center space-x-2">
                              <div className={`w-2 h-2 rounded-full ${
                                user.status === 'online' ? 'bg-green-500' :
                                user.status === 'away' ? 'bg-yellow-500' : 'bg-gray-400'
                              }`}></div>
                              <span className="text-xs text-gray-500 capitalize">{user.status}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-slate-800">
                  <Shield className="h-5 w-5 text-green-600" />
                  <span>Security & Privacy</span>
                </CardTitle>
                <CardDescription>
                  Enterprise-grade security with end-to-end encryption and audit trails
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold text-gray-800">Data Protection</h4>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>AES-256 encryption at rest</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>TLS 1.3 encryption in transit</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Zero-trust architecture</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Complete audit trails</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="font-semibold text-gray-800">Compliance</h4>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>GDPR compliant</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>HIPAA ready</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>SOC 2 Type II</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>ISO 27001</span>
                      </div>
                    </div>
                  </div>
                </div>

                {healthStatus && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-3">System Status</h4>
                    <div className="space-y-2">
                      {Object.entries(healthStatus.components).map(([component, status]) => (
                        <div key={component} className="flex items-center justify-between text-sm">
                          <span className="capitalize">{component.replace('_', ' ')}</span>
                          <Badge variant={status === 'healthy' ? 'default' : 'destructive'}>
                            {status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-md mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-600">
            <p className="text-sm">
              Comprende - Breaking down language barriers with AI-powered communication
            </p>
            <p className="text-xs mt-2">
              Secure • Reliable • Universal
            </p>
          </div>
        </div>
      </footer>

      {/* Team Creation Dialog */}
      <Dialog open={showTeamCreator} onOpenChange={setShowTeamCreator}>
        <DialogContent className="center-dialog">
          <DialogHeader className="mb-6">
            <DialogTitle className="text-heading-3">Create New Team</DialogTitle>
            <DialogDescription className="text-body">
              Create a team to collaborate and share files with others
            </DialogDescription>
          </DialogHeader>
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const teamName = formData.get('teamName');
              const teamDescription = formData.get('teamDescription');
              if (teamName) {
                createTeam(teamName, teamDescription);
              }
            }}
            className="space-y-6"
          >
            <div>
              <label className="form-label">Team Name</label>
              <input 
                name="teamName" 
                type="text" 
                placeholder="Enter team name" 
                required 
                className="enhanced-input"
              />
            </div>
            <div>
              <label className="form-label">Description (Optional)</label>
              <textarea 
                name="teamDescription" 
                placeholder="Brief description of your team"
                className="enhanced-textarea"
              />
            </div>
            <div className="flex space-x-3 pt-4">
              <button type="submit" className="flex-1 dialog-button-primary">
                Create Team
              </button>
              <button 
                type="button" 
                onClick={() => setShowTeamCreator(false)}
                className="dialog-button-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Team Join Dialog */}
      <Dialog open={showTeamJoiner} onOpenChange={setShowTeamJoiner}>
        <DialogContent className="center-dialog">
          <DialogHeader className="mb-6">
            <DialogTitle className="text-heading-3">Join Team</DialogTitle>
            <DialogDescription className="text-body">
              Enter the invite code to join an existing team
            </DialogDescription>
          </DialogHeader>
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const inviteCode = formData.get('inviteCode');
              if (inviteCode) {
                joinTeam(inviteCode);
                setShowTeamJoiner(false);
              }
            }}
            className="space-y-6"
          >
            <div>
              <label className="form-label">Invite Code</label>
              <input 
                name="inviteCode" 
                type="text" 
                placeholder="Enter 8-character invite code" 
                required 
                className="enhanced-input"
                maxLength="8"
                style={{letterSpacing: '2px', textTransform: 'uppercase'}}
              />
              <p className="text-caption mt-2 text-[var(--color-text-tertiary)]">
                Ask your team admin for the invite code
              </p>
            </div>
            <div className="flex space-x-3 pt-4">
              <button type="submit" className="flex-1 dialog-button-primary">
                Join Team
              </button>
              <button 
                type="button" 
                onClick={() => setShowTeamJoiner(false)}
                className="dialog-button-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* File Upload Dialog */}
      <Dialog open={showFileUpload} onOpenChange={setShowFileUpload}>
        <DialogContent className="file-upload-dialog">
          <DialogHeader className="mb-6">
            <DialogTitle className="text-heading-3">Upload File to Team</DialogTitle>
            <DialogDescription className="text-body">
              Share a file with your team members
            </DialogDescription>
          </DialogHeader>
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const file = formData.get('file');
              const description = formData.get('description');
              const tags = formData.get('tags');
              if (file && currentTeam) {
                uploadTeamFile(currentTeam.id, file, description, tags);
              }
            }}
            className="space-y-6"
          >
            <div>
              <label className="form-label">File</label>
              <div className="enhanced-file-input-container">
                <input 
                  name="file" 
                  type="file" 
                  required 
                  className="enhanced-file-input"
                  onChange={(e) => {
                    const fileName = e.target.files[0]?.name || '';
                    const fileInfo = document.querySelector('.file-selected-info');
                    if (fileInfo) {
                      fileInfo.textContent = fileName ? `Selected: ${fileName}` : 'No file selected';
                    }
                  }}
                />
                <div className="enhanced-file-button">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Choose File
                </div>
                <div className="file-selected-info">No file selected</div>
              </div>
            </div>
            <div>
              <label className="form-label">Description (Optional)</label>
              <textarea 
                name="description" 
                placeholder="Brief description of the file"
                className="enhanced-textarea"
              />
            </div>
            <div>
              <label className="form-label">Tags (Optional)</label>
              <input 
                name="tags" 
                type="text" 
                placeholder="Comma-separated tags"
                className="enhanced-input"
              />
            </div>
            <div className="flex space-x-3 pt-4">
              <button type="submit" className="flex-1 dialog-button-primary">
                Upload File
              </button>
              <button 
                type="button" 
                onClick={() => setShowFileUpload(false)}
                className="dialog-button-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
      </>
      )}
    </div>
  );
}

// Wrap App with ErrorBoundary
const WrappedApp = () => (
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

export default WrappedApp;