import React from 'react';

interface IconProps {
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  style?: React.CSSProperties;
}

export function Icon({ name, size = 'md', className = '', style }: IconProps): React.ReactElement {
  const sizeClass = size === 'sm' ? 'icon-sm' : size === 'lg' ? 'icon-lg' : '';

  return (
    <span className={`material-symbols-outlined ${sizeClass} ${className}`} style={style}>
      {name}
    </span>
  );
}
