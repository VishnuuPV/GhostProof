import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#080b10",
        panel: "#111722",
        signal: "#38e8a1",
        amber: "#f5b84b",
        danger: "#ff5c75"
      }
    }
  },
  plugins: []
} satisfies Config;
