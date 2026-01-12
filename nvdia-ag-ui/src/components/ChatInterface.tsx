"use client";

import { useState, useRef, useEffect } from "react";
import { NvidiaLogo } from "./NvidiaLogo";

// Helper function to format timestamp consistently
function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
}

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: {
    sources?: string[];
    confidence?: number;
  };
}

interface Suggestion {
  icon: string;
  text: string;
  description: string;
}

const quickSuggestions: Suggestion[] = [
  {
    icon: "📄",
    text: "Search Documents",
    description: "Find retail compliance information",
  },
  {
    icon: "🖼️",
    text: "Search Products",
    description: "Visual search for fashion items",
  },
  {
    icon: "📊",
    text: "Analyze Inventory",
    description: "Get insights on stock levels",
  },
  {
    icon: "💬",
    text: "Customer Support",
    description: "Access support knowledge base",
  },
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isClient, setIsClient] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const threadIdRef = useRef<string>(`thread-${Date.now()}`);

  // Initialize messages on client side only to avoid hydration mismatch
  useEffect(() => {
    setIsClient(true);
    setMessages([
      {
        id: "welcome",
        role: "system",
        content: "Welcome to **NVIDIA Retail AI Agent Team**. I can help you with:\n\n• **Document Search** - Query retail compliance PDFs\n• **Image Search** - Find fashion products visually\n• **Data Analysis** - Inventory and sales insights\n• **Customer Support** - Access support knowledge base\n\nWhat would you like to explore today?",
        timestamp: new Date(),
      },
    ]);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    // Add user message to UI immediately
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call the backend directly, bypassing CopilotKit runtime
      const response = await fetch('http://localhost:8000/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          threadId: threadIdRef.current,
          runId: `run-${Date.now()}`,
          state: {},
          messages: [
            {
              id: userMessage.id,
              role: "user",
              content: userMessage.content,
            }
          ],
          tools: [],
          context: [],
          forwardedProps: {},
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read the streaming response from ADK
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessageId = '';
      let assistantContent = "";
      let messageCreated = false;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter(line => line.trim());

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                // Handle ADK event types
                switch (data.type) {
                  case 'TEXT_MESSAGE_START':
                    // Create assistant message when streaming starts
                    assistantMessageId = data.messageId;
                    if (!messageCreated) {
                      const assistantMessage: Message = {
                        id: assistantMessageId,
                        role: "assistant",
                        content: "",
                        timestamp: new Date(),
                      };
                      setMessages((prev) => [...prev, assistantMessage]);
                      messageCreated = true;
                    }
                    break;

                  case 'TEXT_MESSAGE_CONTENT':
                    // Append content delta
                    if (data.delta) {
                      assistantContent += data.delta;
                      setMessages((prev) =>
                        prev.map((msg) =>
                          msg.id === assistantMessageId
                            ? { ...msg, content: assistantContent }
                            : msg
                        )
                      );
                    }
                    break;

                  case 'TEXT_MESSAGE_END':
                    // Message complete
                    console.log('Message completed:', assistantContent);
                    break;

                  default:
                    // Ignore other events
                    break;
                }
              } catch (e) {
                // Ignore parse errors for non-JSON lines
                console.debug('Parse error:', e);
              }
            }
          }
        }
      }

      // If we didn't get any content, show an error
      if (!assistantContent && !messageCreated) {
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "I received your message but couldn't generate a response. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorDetails = error instanceof Error ? error.message : String(error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `Sorry, I encountered an error: ${errorDetails}\n\nPlease make sure:\n• Backend is running on port 8000\n• You have a GOOGLE_API_KEY set\n• Check the browser console for details`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    setInput(suggestion.text);
    textareaRef.current?.focus();
  };

  const formatContent = (content: string) => {
    // Basic markdown-like formatting
    return content
      .split("\n")
      .map((line, i) => {
        // Bold text
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-nvidia-green font-semibold">$1</strong>');
        // Bullet points
        if (line.trim().startsWith("•")) {
          return `<div key="${i}" class="flex gap-2 my-1.5"><span class="text-nvidia-green">•</span><span>${line.substring(1)}</span></div>`;
        }
        return `<div key="${i}" class="my-1.5 leading-relaxed">${line || "<br/>"}</div>`;
      })
      .join("");
  };

  // Show minimal loading state during SSR
  if (!isClient) {
    return (
      <div className="flex flex-col h-screen bg-nvidia-dark">
        <header className="bg-nvidia-dark-surface/80 backdrop-blur-md border-b border-nvidia-border/50 px-6 py-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-4">
            <NvidiaLogo className="w-32 h-8 text-white" />
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 rounded-full border-2 border-nvidia-green border-t-transparent animate-spin" />
            <div className="text-nvidia-text-muted font-medium tracking-wide text-sm">INITIALIZING AI CORE...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="flex-1 flex flex-col h-screen relative bg-nvidia-dark overflow-hidden">
      {/* Ambient Background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-nvidia-green/5 rounded-full blur-[120px] opacity-50 mix-blend-screen animate-pulse-slow" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-nvidia-purple/5 rounded-full blur-[120px] opacity-30 mix-blend-screen" />
      </div>

      {/* Header */}
      <header className="h-16 flex-shrink-0 border-b border-nvidia-border/50 glass flex items-center justify-between px-6 relative z-10">
        <div className="flex items-center gap-4">
          <NvidiaLogo className="w-28 h-auto text-nvidia-text" />
          <div className="h-5 w-px bg-nvidia-border" />
          <span className="text-nvidia-text-muted text-sm font-medium tracking-wide">Retail AI Agent</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-nvidia-green/10 border border-nvidia-green/20">
            <div className="w-2 h-2 rounded-full bg-nvidia-green animate-pulse" />
            <span className="text-xs font-semibold text-nvidia-green tracking-wide uppercase">Powered by NVIDIA AI</span>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar relative z-0">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`flex gap-4 ${message.role === "user" ? "flex-row-reverse" : "flex-row"
                } animate-fade-in`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Avatar */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${message.role === "user"
                  ? "bg-gradient-to-br from-nvidia-green to-nvidia-green-hover"
                  : "bg-nvidia-dark-surface border border-nvidia-border"
                }`}>
                {message.role === "user" ? (
                  <svg className="w-4 h-4 text-nvidia-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-nvidia-green" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
                  </svg>
                )}
              </div>

              {/* Message Content */}
              <div className={`flex flex-col max-w-[80%] ${message.role === "user" ? "items-end" : "items-start"}`}>
                <div className="flex items-center gap-2 mb-1 px-1">
                  <span className="text-xs font-medium text-nvidia-text-muted">
                    {message.role === "user" ? "You" : "NVIDIA AI"}
                  </span>
                  <span className="text-[10px] text-nvidia-text-muted/60">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                <div
                  className={`relative px-5 py-3.5 rounded-2xl shadow-md text-sm leading-relaxed ${message.role === "user"
                      ? "bg-gradient-to-br from-nvidia-green to-nvidia-green-hover text-nvidia-dark font-medium rounded-tr-none shadow-glow-green-sm"
                      : "bg-nvidia-dark-surface border border-nvidia-border/50 text-nvidia-text rounded-tl-none"
                    }`}
                >
                  <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-strong:text-inherit">
                    <div dangerouslySetInnerHTML={{ __html: formatContent(message.content) }} />
                  </div>

                  {/* Confidence Score (Mock) */}
                  {message.role === "assistant" && (
                    <div className="mt-3 pt-2 border-t border-nvidia-border/30 flex items-center gap-2">
                      <div className="flex items-center gap-1 text-[10px] text-nvidia-text-muted uppercase tracking-wider font-semibold">
                        <svg className="w-3 h-3 text-nvidia-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Confidence: High
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex gap-4 animate-fade-in">
              <div className="w-8 h-8 rounded-full bg-nvidia-dark-surface border border-nvidia-border flex items-center justify-center">
                <svg className="w-5 h-5 text-nvidia-green animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 mb-1 px-1">
                  <span className="text-xs font-medium text-nvidia-text-muted">NVIDIA AI</span>
                </div>
                <div className="px-5 py-3 rounded-2xl rounded-tl-none bg-nvidia-dark-surface border border-nvidia-border/50 shadow-sm flex items-center gap-3">
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-nvidia-green rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                    <div className="w-1.5 h-1.5 bg-nvidia-green rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
                    <div className="w-1.5 h-1.5 bg-nvidia-green rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
                  </div>
                  <span className="text-sm text-nvidia-text-muted font-medium">Processing...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 px-4 sm:px-6 pb-6 pt-4 relative z-20">
        <div className="max-w-3xl mx-auto">
          {/* Quick Suggestions (Only show when empty) */}
          {messages.length === 1 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 animate-slide-up">
              {[
                { icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z", label: "Analyze Report", desc: "Upload & summarize PDF" },
                { icon: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z", label: "Image Search", desc: "Find products by photo" },
                { icon: "M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z", label: "Sales Trends", desc: "View performance data" },
                { icon: "M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z", label: "Support Help", desc: "Query knowledge base" },
              ].map((item, i) => (
                <button
                  key={i}
                  onClick={() => setInput(item.label)}
                  className="group flex flex-col items-center text-center p-3 rounded-xl bg-nvidia-dark-surface border border-nvidia-border hover:border-nvidia-green/50 hover:bg-nvidia-dark-elevated transition-all duration-200 shadow-sm hover:shadow-md hover:-translate-y-0.5"
                >
                  <div className="p-2 rounded-lg bg-nvidia-dark-elevated group-hover:bg-nvidia-green/10 text-nvidia-text-muted group-hover:text-nvidia-green transition-colors mb-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                  </div>
                  <span className="text-xs font-semibold text-nvidia-text group-hover:text-white transition-colors">{item.label}</span>
                </button>
              ))}
            </div>
          )}

          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-nvidia-green/20 to-nvidia-purple/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
            <div className="relative flex items-end gap-2 bg-nvidia-dark-surface/80 backdrop-blur-md border border-nvidia-border rounded-2xl p-2 shadow-2xl focus-within:border-nvidia-green/50 focus-within:ring-1 focus-within:ring-nvidia-green/20 transition-all duration-200">
              <button className="p-2.5 text-nvidia-text-muted hover:text-nvidia-text hover:bg-nvidia-dark-elevated rounded-xl transition-colors" title="Attach file">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </button>

              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask anything about retail data, inventory, or support..."
                className="flex-1 bg-transparent text-nvidia-text placeholder-nvidia-text-muted/50 text-sm px-2 py-3 focus:outline-none resize-none max-h-48 custom-scrollbar"
                rows={1}
              />

              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className={`p-2.5 rounded-xl transition-all duration-200 flex-shrink-0 ${input.trim() && !isLoading
                    ? "bg-nvidia-green text-nvidia-dark hover:bg-nvidia-green-hover shadow-lg shadow-nvidia-green/20"
                    : "bg-nvidia-dark-elevated text-nvidia-text-muted cursor-not-allowed"
                  }`}
              >
                <svg className="w-5 h-5 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19V5m0 0l-7 7m7-7l7 7" />
                </svg>
              </button>
            </div>
            <div className="text-center mt-3">
              <p className="text-[10px] text-nvidia-text-muted/60">
                NVIDIA AI can make mistakes. Please review sensitive information.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
