import { motion } from 'framer-motion';
import useTheme from '../../hooks/useTheme';

export function AuroraBackground() {
  const { isDark } = useTheme();

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 bg-[#f6faf7] dark:bg-[#04130a] transition-colors duration-500">
      {/* Aurora glow blobs - adapts opacity and colors dynamically */}
      <motion.div
        animate={{
          x: [0, 60, -30, 0],
          y: [0, -50, 40, 0],
          scale: [1, 1.15, 0.9, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -top-[10%] -left-[10%] w-[60vw] h-[60vw] rounded-full bg-primary-500/5 dark:bg-primary-500/10 blur-[130px]"
      />
      <motion.div
        animate={{
          x: [0, -40, 50, 0],
          y: [0, 60, -30, 0],
          scale: [1, 0.9, 1.1, 1],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -bottom-[10%] -right-[10%] w-[60vw] h-[60vw] rounded-full bg-accent-500/5 dark:bg-accent-500/10 blur-[130px]"
      />
      <motion.div
        animate={{
          x: [0, 30, -30, 0],
          y: [0, 30, -30, 0],
          opacity: isDark ? [0.3, 0.6, 0.3] : [0.1, 0.2, 0.1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-[30%] left-[20%] w-[40vw] h-[40vw] rounded-full bg-emerald-500/[0.02] dark:bg-emerald-500/5 blur-[150px]"
      />
    </div>
  );
}

export default AuroraBackground;
