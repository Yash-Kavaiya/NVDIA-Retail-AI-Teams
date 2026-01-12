import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        nvidia: {
          green: "#76B900",
          "green-hover": "#66a100", // Slightly darker for hover, more natural
          "green-dim": "rgba(118, 185, 0, 0.08)",
          dark: "#0D0D0D", // Deep charcoal, not pitch black
          "dark-surface": "#161616", // Lighter surface
          "dark-elevated": "#1F1F1F", // For cards/modals
          text: "#F5F5F5", // Off-white for better readability
          "text-muted": "#9CA3AF", // Cool gray
          border: "#2D2D2D",
          "border-light": "#3D3D3D",
          purple: "#9b6bff",
          red: "#ff5757",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          "sans-serif",
        ],
      },
      boxShadow: {
        'glow-green': '0 0 15px rgba(118, 185, 0, 0.2)',
        'glow-green-sm': '0 0 8px rgba(118, 185, 0, 0.15)',
        'glass': '0 4px 20px 0 rgba(0, 0, 0, 0.25)',
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'nvidia-gradient': 'linear-gradient(135deg, #76B900 0%, #5d9200 100%)',
        'dark-gradient': 'linear-gradient(to bottom, #161616, #0D0D0D)',
      },
      animation: {
        bounce: "bounce 1s infinite",
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        bounce: {
          "0%, 100%": {
            transform: "translateY(-25%)",
            animationTimingFunction: "cubic-bezier(0.8, 0, 1, 1)",
          },
          "50%": {
            transform: "translateY(0)",
            animationTimingFunction: "cubic-bezier(0, 0, 0.2, 1)",
          },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
