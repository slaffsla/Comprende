import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import { 
  Globe, Languages, FileText, Users, Shield, Zap, 
  Mic, MicOff, Volume2, Copy, Download, Upload, Camera, 
  Settings, Bell, User, Search, Plus, Send, Pause, 
  Video, PhoneOff, Share  
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
  const [localStream, setLocalStream] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  
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
      } catch (error) {
        console.error('Failed to save user:', error);
      }
    } else {
      localStorage.removeItem('comprende-user');
      setShowLogin(true);
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

  const loadUserData = async () => {
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
        setDetectedLanguage(response.data.source_language);
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
      // Try modern Clipboard API first
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard");
      } else {
        // Fallback for older browsers or restricted environments
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          document.execCommand('copy');
          toast.success("Copied to clipboard");
        } catch (err) {
          console.error('Fallback copy failed:', err);
          toast.error("Copy not supported in this environment");
        }
        
        document.body.removeChild(textArea);
      }
    } catch (error) {
      console.error('Copy failed:', error);
      // Create a temporary input for manual copy
      const input = document.createElement('input');
      input.value = text;
      document.body.appendChild(input);
      input.select();
      toast.info("Text selected - press Ctrl+C (Cmd+C on Mac) to copy");
      setTimeout(() => document.body.removeChild(input), 5000);
    }
  };

  const speakText = (text, lang) => {
    if ('speechSynthesis' in window) {
      // Stop any ongoing speech
      speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Map language codes to speech synthesis languages
      const langMap = {
        'heb': 'he-IL',
        'ara': 'ar-SA',
        'spa': 'es-ES',
        'fra': 'fr-FR',
        'deu': 'de-DE',
        'ita': 'it-IT',
        'por': 'pt-PT',
        'rus': 'ru-RU',
        'chi': 'zh-CN',
        'jpn': 'ja-JP',
        'kor': 'ko-KR',
        'hin': 'hi-IN',
        'tur': 'tr-TR'
      };
      
      utterance.lang = langMap[lang] || 'en-US';
      utterance.rate = 0.9;
      utterance.pitch = 1;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => {
        setIsSpeaking(false);
        toast.error("Speech synthesis failed");
      };
      
      speechSynthesis.speak(utterance);
    } else {
      toast.error("Speech synthesis not supported");
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
      // Use backend download endpoint for better reliability
      const response = await axios.post(`${BACKEND_URL}/api/documents/download`, {
        content: content,
        filename: filename
      }, {
        responseType: 'blob'
      });

      // Create download link
      const blob = new Blob([response.data], { type });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast.success("File downloaded successfully");
    } catch (error) {
      console.error('Download failed:', error);
      // Fallback to client-side download
      try {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        toast.success("File downloaded successfully");
      } catch (fallbackError) {
        console.error('Fallback download failed:', fallbackError);
        toast.error("Download failed");
      }
    }
  };

  const createMeeting = async () => {
    try {
      setIsLoading(true);
      const meetingId = `meeting-${Date.now()}`;
      
      // Create meeting in backend first
      const response = await axios.post(`${BACKEND_URL}/api/meetings`, {
        name: "Translation Meeting",
        participants: ["demo-user"]
      });
      
      if (response.data) {
        const newMeeting = {
          id: response.data.id || meetingId,
          name: response.data.name || "Translation Meeting",
          participants: response.data.participants || ["demo-user"],
          createdAt: new Date(),
          status: "active"
        };
        
        setMeetings(prev => [...prev, newMeeting]);
        
        // Switch to collaborate tab to show the meeting
        setActiveTab("collaborate");
        
        toast.success("Meeting created successfully! Click 'Join Video' to start video call.");
        
        // Auto-initialize WebRTC after a short delay
        setTimeout(() => {
          initializeWebRTC(newMeeting.id);
        }, 1000);
      }
      
    } catch (error) {
      console.error('Failed to create meeting:', error);
      // Fallback to client-side meeting creation
      const meetingId = `meeting-${Date.now()}`;
      const newMeeting = {
        id: meetingId,
        name: "Translation Meeting",
        participants: ["demo-user"],
        createdAt: new Date(),
        status: "active"
      };
      setMeetings(prev => [...prev, newMeeting]);
      setActiveTab("collaborate");
      toast.success("Meeting created successfully! Click 'Join Video' to start video call.");
    } finally {
      setIsLoading(false);
    }
  };

  const initializeWebRTC = async (meetingId) => {
    try {
      setIsLoading(true);
      
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast.error("Your browser doesn't support camera/microphone access. Please use a modern browser.");
        return;
      }

      // Get user media (video + audio)
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      // Set up local video preview
      setLocalStream(stream);
      
      // Show local video immediately
      setTimeout(() => {
        const videoElement = document.getElementById('local-video');
        if (videoElement && stream) {
          videoElement.srcObject = stream;
          videoElement.play().catch(e => console.log('Video play failed:', e));
        }
      }, 100);
      
      toast.success("✅ Camera and microphone connected successfully!");
      
    } catch (error) {
      console.error('WebRTC initialization failed:', error);
      let errorMessage = "Failed to access camera/microphone";
      
      if (error.name === 'NotAllowedError') {
        errorMessage = "🚫 Camera/microphone permission denied. Please allow access and try again.";
      } else if (error.name === 'NotFoundError') {
        errorMessage = "📷 No camera/microphone found. Please connect a device and try again.";
      } else if (error.name === 'NotReadableError') {
        errorMessage = "🔒 Camera/microphone is already in use by another application.";
      } else if (error.name === 'OverconstrainedError') {
        errorMessage = "⚙️ Camera settings not supported. Trying with default settings...";
        
        // Retry with basic constraints
        try {
          const basicStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
          });
          setLocalStream(basicStream);
          toast.success("✅ Connected with basic camera settings!");
        } catch (retryError) {
          toast.error("❌ Failed to connect even with basic settings.");
        }
      } else {
        errorMessage = `❌ WebRTC error: ${error.message}`;
      }
      
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const joinMeeting = (meetingId) => {
    initializeWebRTC(meetingId);
  };

  const leaveMeeting = () => {
    if (localStream) {
      // Stop all tracks (video and audio)
      localStream.getTracks().forEach(track => {
        track.stop();
        console.log(`Stopped ${track.kind} track - readyState: ${track.readyState}`);
      });
      
      // Clear the stream reference
      setLocalStream(null);
      
      // Clear the video element
      const videoElement = document.getElementById('local-video');
      if (videoElement) {
        videoElement.srcObject = null;
        videoElement.load(); // Force reload to clear the video
      }
      
      console.log("All media tracks stopped and cleared");
    }
    
    // Also remove the meeting from active meetings list
    setMeetings(prev => prev.filter(meeting => !localStream));
    
    toast.success("✅ Left the meeting successfully. Camera and microphone turned off.");
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Toaster position="top-right" />
      
      {/* Login Dialog */}
      {showLogin && (
        <Dialog open={showLogin} onOpenChange={() => {}}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Globe className="h-6 w-6 text-blue-600" />
                <span>Welcome to Comprende</span>
              </DialogTitle>
              <p className="text-sm text-gray-600">
                Enter your details to start translating and collaborating
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
                <label className="text-sm font-medium">Name</label>
                <Input name="name" type="text" placeholder="Your name" required />
              </div>
              <div>
                <label className="text-sm font-medium">Email</label>
                <Input name="email" type="email" placeholder="your@email.com" required />
              </div>
              <div>
                <label className="text-sm font-medium">Avatar</label>
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
                    className="mb-2"
                  />
                  <input type="hidden" name="avatar" id="avatar-data" />
                  <img 
                    id="avatar-preview" 
                    style={{display: 'none'}} 
                    className="w-10 h-10 rounded-full object-cover border" 
                    alt="Avatar preview"
                  />
                  <p className="text-xs text-gray-500">
                    Upload an image (max 1MB) or we'll use your Gravatar
                  </p>
                </div>
              </div>
              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
                Start Using Comprende
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      )}
      
      {/* Main App Content - Only show when logged in */}
      {!showLogin && currentUser && (
        <>
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">Comprende</h1>
                <p className="text-xs sm:text-sm text-gray-600">Universal Communication Platform</p>
              </div>
              <div className="sm:hidden">
                <h1 className="text-lg font-bold text-gray-900">Comprende</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 sm:space-x-4">
              {healthStatus?.status && (
                <Badge 
                  variant={healthStatus.status === "healthy" ? "default" : "destructive"} 
                  className="text-xs hidden sm:inline-flex bg-green-100 text-green-800 border-green-300"
                >
                  <div className="flex items-center space-x-1">
                    <div className={`w-2 h-2 rounded-full ${
                      healthStatus.status === "healthy" ? "bg-green-500" : "bg-red-500"
                    }`}></div>
                    <span>System {healthStatus.status}</span>
                  </div>
                </Badge>
              )}
              
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="relative">
                    <Bell className="h-4 w-4" />
                    {notifications.length > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {notifications.length}
                      </span>
                    )}
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Notifications</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-3">
                    {notifications.length > 0 ? (
                      <>
                        {notifications.map(notification => (
                          <div key={notification.id} className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm">{notification.message}</p>
                            <p className="text-xs text-gray-500">{notification.time}</p>
                          </div>
                        ))}
                        <Button onClick={clearNotifications} variant="outline" className="w-full">
                          Clear All
                        </Button>
                      </>
                    ) : (
                      <p className="text-gray-500 text-center">No notifications</p>
                    )}
                  </div>
                </DialogContent>
              </Dialog>

              <Dialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Settings</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Default Source Language</label>
                      <Select 
                        value={settings.defaultSourceLang} 
                        onValueChange={(value) => {
                          setSettings(prev => ({...prev, defaultSourceLang: value}));
                          setSourceLang(value);
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="auto">Auto-detect</SelectItem>
                          {Object.entries(LANGUAGES).map(([code, name]) => (
                            <SelectItem key={code} value={code}>{name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Default Target Language</label>
                      <Select 
                        value={settings.defaultTargetLang}
                        onValueChange={(value) => {
                          setSettings(prev => ({...prev, defaultTargetLang: value}));
                          setTargetLang(value);
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(LANGUAGES).map(([code, name]) => (
                            <SelectItem key={code} value={code}>{name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Voice Settings</label>
                      <div className="space-y-2 mt-2">
                        <label className="flex items-center">
                          <input 
                            type="checkbox" 
                            className="mr-2" 
                            checked={settings.voiceInputEnabled}
                            onChange={(e) => setSettings(prev => ({...prev, voiceInputEnabled: e.target.checked}))}
                          />
                          Enable voice input
                        </label>
                        <label className="flex items-center">
                          <input 
                            type="checkbox" 
                            className="mr-2" 
                            checked={settings.voiceOutputEnabled}
                            onChange={(e) => setSettings(prev => ({...prev, voiceOutputEnabled: e.target.checked}))}
                          />
                          Enable voice output
                        </label>
                        <label className="flex items-center">
                          <input 
                            type="checkbox" 
                            className="mr-2" 
                            checked={settings.autoTranslateVoice}
                            onChange={(e) => setSettings(prev => ({...prev, autoTranslateVoice: e.target.checked}))}
                          />
                          Auto-translate voice input
                        </label>
                      </div>
                    </div>
                    <div className="pt-4 border-t">
                      <Button 
                        variant="outline" 
                        className="w-full"
                        onClick={() => {
                          const defaultSettings = {
                            voiceInputEnabled: true,
                            voiceOutputEnabled: true,
                            autoTranslateVoice: false,
                            defaultSourceLang: 'auto',
                            defaultTargetLang: 'eng'
                          };
                          setSettings(defaultSettings);
                          setSourceLang('auto');
                          setTargetLang('eng');
                          toast.success("Settings reset to defaults");
                        }}
                      >
                        Reset to Defaults
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="flex items-center space-x-2">
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
                      <span className="text-lg">👤</span>
                    )}
                    <span className="text-lg" style={{display: 'none'}}>👤</span>
                    <span className="hidden sm:inline text-sm">{currentUser.name}</span>
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>User Profile</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      {currentUser.avatar && currentUser.avatar.startsWith('data:') ? (
                        <img 
                          src={currentUser.avatar} 
                          alt="User avatar" 
                          className="w-12 h-12 rounded-full object-cover border"
                        />
                      ) : currentUser.avatar && currentUser.avatar.startsWith('http') ? (
                        <img 
                          src={currentUser.avatar} 
                          alt="User avatar" 
                          className="w-12 h-12 rounded-full object-cover border"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'inline';
                          }}
                        />
                      ) : (
                        <span className="text-3xl">👤</span>
                      )}
                      <span className="text-3xl" style={{display: 'none'}}>👤</span>
                      <div>
                        <p className="font-medium">{currentUser.name}</p>
                        <p className="text-sm text-gray-500">{currentUser.email}</p>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Update Avatar</label>
                      <Input 
                        type="file" 
                        accept="image/*" 
                        onChange={handleAvatarUpload}
                        className="mt-1"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Upload a new avatar image (max 1MB)
                      </p>
                    </div>
                    <div className="pt-4 border-t">
                      <Button onClick={logoutUser} variant="outline" className="w-full">
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
                          <SelectTrigger>
                            <SelectValue placeholder="Source Language" />
                          </SelectTrigger>
                          <SelectContent className="max-h-60 overflow-y-auto bg-white border-gray-200 shadow-lg">
                            <SelectItem value="auto" className="font-medium text-gray-900 hover:bg-blue-50 hover:text-blue-700">
                              Auto-detect
                            </SelectItem>
                            {Object.entries(LANGUAGES)
                              .sort(([,a], [,b]) => a.localeCompare(b))
                              .map(([code, name]) => (
                              <SelectItem 
                                key={code} 
                                value={code}
                                className="text-gray-900 hover:bg-blue-50 hover:text-blue-700 focus:bg-blue-100 focus:text-blue-800"
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
                          <SelectTrigger>
                            <SelectValue placeholder="Target Language" />
                          </SelectTrigger>
                          <SelectContent className="max-h-60 overflow-y-auto">
                            {Object.entries(LANGUAGES).map(([code, name]) => (
                              <SelectItem key={code} value={code}>{name}</SelectItem>
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
                              {LANGUAGES[documentResult.detected_language]} → English
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
                          onClick={() => downloadFile(documentResult.extracted_text, `${documentResult.filename}_original.txt`)}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download Original
                        </Button>
                        {documentResult.translated_text && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => downloadFile(documentResult.translated_text, `${documentResult.filename}_translated.txt`)}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download Translation
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
              {/* Main Collaboration Area */}
              <div className="lg:col-span-2 space-y-6">
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-slate-800">
                      <Users className="h-5 w-5 text-blue-600" />
                      <span>Team Collaboration</span>
                    </CardTitle>
                    <CardDescription>
                      Real-time communication with live translation
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex space-x-4">
                      <Button onClick={createMeeting} className="bg-green-600 hover:bg-green-700">
                        <Plus className="h-4 w-4 mr-2" />
                        Start New Meeting
                      </Button>
                      <Button variant="outline">
                        <Search className="h-4 w-4 mr-2" />
                        Join Meeting
                      </Button>
                    </div>

                    {/* Active Meetings with Video Interface */}
                    {meetings.length > 0 && (
                      <div className="space-y-3">
                        <h3 className="font-semibold">Active Meetings</h3>
                        {meetings.map(meeting => (
                          <div key={meeting.id} className="p-4 border rounded-lg">
                            <div className="flex items-center justify-between mb-3">
                              <div>
                                <h4 className="font-medium">{meeting.name}</h4>
                                <p className="text-sm text-gray-500">
                                  {meeting.participants?.length || 0} participants
                                </p>
                              </div>
                              <div className="flex space-x-2">
                                <Button 
                                  size="sm" 
                                  onClick={() => joinMeeting(meeting.id)}
                                  disabled={isLoading}
                                >
                                  {isLoading ? (
                                    <span className="flex items-center">
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                                      Connecting...
                                    </span>
                                  ) : (
                                    <>
                                      <Video className="h-4 w-4 mr-1" />
                                      Join Video
                                    </>
                                  )}
                                </Button>
                                <Button variant="outline" size="sm" title="Mute/Unmute">
                                  <Mic className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            
                            {/* Video Interface */}
                            {localStream && (
                              <div className="mt-4 p-4 bg-gray-900 rounded-lg">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div className="relative">
                                    <video
                                      id="local-video"
                                      autoPlay
                                      muted
                                      playsInline
                                      className="w-full h-48 bg-gray-800 rounded-lg object-cover"
                                    />
                                    <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                                      You
                                    </div>
                                  </div>
                                  <div className="relative">
                                    <div className="w-full h-48 bg-gray-800 rounded-lg flex items-center justify-center text-gray-400">
                                      <div className="text-center">
                                        <Users className="h-8 w-8 mx-auto mb-2" />
                                        <p className="text-sm">Waiting for participants...</p>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Meeting Controls */}
                                <div className="flex items-center justify-center space-x-4 mt-4">
                                  <Button variant="outline" size="sm" className="flex items-center space-x-2">
                                    <Mic className="h-4 w-4" />
                                    <span className="text-sm">Mute</span>
                                  </Button>
                                  <Button variant="outline" size="sm" className="flex items-center space-x-2">
                                    <Video className="h-4 w-4" />
                                    <span className="text-sm">Camera</span>
                                  </Button>
                                  <Button 
                                    variant="destructive" 
                                    size="sm"
                                    onClick={leaveMeeting}
                                    className="flex items-center space-x-2"
                                  >
                                    <PhoneOff className="h-4 w-4" />
                                    <span className="text-sm">Leave</span>
                                  </Button>
                                  <Button variant="outline" size="sm" className="flex items-center space-x-2">
                                    <Share className="h-4 w-4" />
                                    <span className="text-sm">Share Screen</span>
                                  </Button>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Shared Files */}
                    {sharedFiles.length > 0 && (
                      <div className="space-y-3">
                        <h3 className="font-semibold">Shared Files</h3>
                        {sharedFiles.map(file => (
                          <div key={file.id} className="p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium">{file.name}</p>
                                <p className="text-sm text-gray-500">
                                  Shared by {file.sharedBy}
                                </p>
                              </div>
                              <Button variant="outline" size="sm">
                                <Download className="h-4 w-4" />
                              </Button>
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
      </>
      )}
    </div>
  );
}

export default App;