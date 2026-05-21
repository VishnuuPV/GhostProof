import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#070a0f",
        panel: "#101722",
        line: "#253044",
        signal: "#38e8a1",
        amber: "#f2b84b",
        danger: "#ff5c75",
        cobalt: "#55a7ff"
      },
      boxShadow: {
        glow: "0 0 30px rgba(56, 232, 161, 0.18)"
      }
    }
  },
  plugins: []
};

export default config;
