import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Camera, Upload, Languages, Shield, Users, FileText, Mic, MicOff, Volume2, Copy, Download, Settings, Bell, User, Globe, Zap } from "lucide-react";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { Separator } from "./components/ui/separator";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Language options
const LANGUAGES = {
  eng: "English",
  spa: "Spanish", 
  heb: "Hebrew",
  ara: "Arabic",
  fra: "French",
  deu: "German",
  ita: "Italian",
  por: "Portuguese",
  rus: "Russian",
  chi: "Chinese"
};

const INDUSTRIES = {
  general: "General",
  healthcare: "Healthcare",
  construction: "Construction", 
  banking: "Banking",
  government: "Government",
  education: "Education",
  legal: "Legal",
  technology: "Technology"
};

function App() {
  const [activeTab, setActiveTab] = useState("translate");
  const [sourceText, setSourceText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [sourceLang, setSourceLang] = useState("auto");
  const [targetLang, setTargetLang] = useState("eng");
  const [context, setContext] = useState("general");
  const [industry, setIndustry] = useState("general");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [file, setFile] = useState(null);
  const [documentResult, setDocumentResult] = useState(null);
  const [translationHistory, setTranslationHistory] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);

  // Check system health on load
  useEffect(() => {
    checkHealth();
    loadTranslationHistory();
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

  const handleTranslate = async () => {
    if (!sourceText.trim()) {
      toast.error("Please enter text to translate");
      return;
    }

    setIsLoading(true);
    setTranslatedText(""); // Clear previous result
    
    try {
      console.log("Starting translation request...");
      const requestBody = {
        text: sourceText,
        source_language: sourceLang === "auto" ? null : sourceLang,
        target_language: targetLang,
        context: context,
        industry: industry
      };
      
      console.log("Request body:", requestBody);
      console.log("API URL:", `${API}/translate`);
      
      const response = await axios.post(`${API}/translate`, requestBody, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000 // 30 second timeout
      });

      console.log("Translation response:", response.data);
      
      if (response.data && response.data.translated_text) {
        setTranslatedText(response.data.translated_text);
        toast.success(`Translation completed with ${(response.data.confidence * 100).toFixed(1)}% confidence`);
        loadTranslationHistory(); // Refresh history
      } else {
        toast.error("Invalid response from translation service");
      }
    } catch (error) {
      console.error("Translation failed:", error);
      if (error.response) {
        // Server responded with error status
        toast.error(`Translation failed: ${error.response.data?.detail || error.response.statusText}`);
      } else if (error.request) {
        // Request was made but no response received
        toast.error("Translation failed: No response from server");
      } else {
        // Something else happened
        toast.error(`Translation failed: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
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
    formData.append("languages", "eng,heb,ara");
    formData.append("translate_to", targetLang);

    try {
      const response = await axios.post(`${API}/documents/process`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setDocumentResult(response.data);
      toast.success("Document processed successfully");
    } catch (error) {
      console.error("Document processing failed:", error);
      toast.error("Document processing failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  const speakText = (text, lang) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang === 'heb' ? 'he-IL' : lang === 'ara' ? 'ar-SA' : 'en-US';
      speechSynthesis.speak(utterance);
    }
  };

  // Mock voice recognition
  const toggleVoiceInput = () => {
    setIsListening(!isListening);
    if (!isListening) {
      toast.info("Voice input activated (mock)");
      // In real implementation, would use Web Speech API
      setTimeout(() => {
        setSourceText("This is mock voice input text");
        setIsListening(false);
        toast.success("Voice input captured");
      }, 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Comprende</h1>
                <p className="text-sm text-gray-600">Universal Communication Platform</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant={healthStatus?.status === "healthy" ? "default" : "destructive"} className="text-xs">
                {healthStatus?.status || "checking..."}
              </Badge>
              <Button variant="ghost" size="sm">
                <Bell className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <User className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="translate" className="flex items-center space-x-2">
              <Languages className="h-4 w-4" />
              <span>Translate</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Documents</span>
            </TabsTrigger>
            <TabsTrigger value="collaborate" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Collaborate</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span>Security</span>
            </TabsTrigger>
          </TabsList>

          {/* Translation Tab */}
          <TabsContent value="translate" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Translation Interface */}
              <div className="lg:col-span-2">
                <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-slate-800">
                      <Zap className="h-5 w-5 text-blue-600" />
                      <span>Real-time Translation</span>
                    </CardTitle>
                    <CardDescription>
                      Translate text between multiple languages with AI-powered context awareness
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Language Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Select value={sourceLang} onValueChange={setSourceLang}>
                        <SelectTrigger>
                          <SelectValue placeholder="Source Language" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="auto">Auto-detect</SelectItem>
                          {Object.entries(LANGUAGES).map(([code, name]) => (
                            <SelectItem key={code} value={code}>{name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      <Button variant="ghost" className="flex items-center justify-center">
                        <Languages className="h-4 w-4" />
                      </Button>

                      <Select value={targetLang} onValueChange={setTargetLang}>
                        <SelectTrigger>
                          <SelectValue placeholder="Target Language" />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(LANGUAGES).map(([code, name]) => (
                            <SelectItem key={code} value={code}>{name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
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
                        <SelectContent>
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
                          className="min-h-32 resize-none pr-12"
                          dir={sourceLang === 'heb' || sourceLang === 'ara' ? 'rtl' : 'ltr'}
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          className="absolute bottom-2 right-2"
                          onClick={toggleVoiceInput}
                        >
                          {isListening ? <MicOff className="h-4 w-4 text-red-500" /> : <Mic className="h-4 w-4" />}
                        </Button>
                      </div>

                      <Button 
                        onClick={handleTranslate} 
                        disabled={isLoading || !sourceText.trim()}
                        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                      >
                        {isLoading ? "Translating..." : "Translate"}
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
                            >
                              <Volume2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions & History */}
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
                    <Button variant="outline" className="w-full justify-start">
                      <Mic className="h-4 w-4 mr-2" />
                      Voice Translation
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={() => setActiveTab("collaborate")}>
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
                      accept=".pdf,.jpg,.jpeg,.png,.txt,.docx"
                      onChange={(e) => setFile(e.target.files[0])}
                      className="max-w-xs mx-auto"
                    />
                  </div>
                </div>

                {file && (
                  <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <span className="font-medium text-blue-900">{file.name}</span>
                    </div>
                    <Button onClick={handleDocumentUpload} disabled={isLoading}>
                      {isLoading ? "Processing..." : "Process Document"}
                    </Button>
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
                        <h4 className="font-medium mb-2">Extracted Text:</h4>
                        <div className="p-3 bg-gray-50 rounded border max-h-40 overflow-y-auto">
                          <p className="text-sm">{documentResult.extracted_text}</p>
                        </div>
                      </div>

                      {documentResult.translated_text && (
                        <div>
                          <h4 className="font-medium mb-2">Translated Text:</h4>
                          <div className="p-3 bg-blue-50 rounded border max-h-40 overflow-y-auto">
                            <p className="text-sm">{documentResult.translated_text}</p>
                          </div>
                        </div>
                      )}

                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm" onClick={() => copyToClipboard(documentResult.extracted_text)}>
                          <Copy className="h-4 w-4 mr-1" />
                          Copy Text
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Collaborate Tab */}
          <TabsContent value="collaborate" className="space-y-6">
            <div className="text-center py-12">
              <Users className="h-16 w-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Team Collaboration</h3>
              <p className="text-gray-500 mb-6">
                Real-time group chats, file sharing, and multi-user conferencing with live translation
              </p>
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-600">
                Coming Soon
              </Button>
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
    </div>
  );
}

export default App;