/**
 * Reusable Card Component
 * =======================
 */

export function Card({
  children,
  className = '',
  onClick,
  ...props
}) {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border border-surface-200 bg-white shadow-soft dark:border-white/10 dark:bg-white/[0.04] backdrop-blur-md p-6 transition-all duration-300 ${
        onClick ? 'cursor-pointer hover:shadow-glow-sm hover:border-primary-500/35 hover:translate-y-[-2px]' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export default Card;
