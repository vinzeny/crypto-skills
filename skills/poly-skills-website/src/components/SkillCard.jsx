import React from 'react';
import { BarChart3, Users, TrendingUp, Layout, Database, Activity, Globe, Zap, Search, Box, ArrowRight, Clock } from 'lucide-react';

const iconMap = {
  BarChart3,
  Users,
  TrendingUp,
  Layout,
  Database,
  Activity,
  Globe,
  Zap,
  Search,
  Box
};

function SkillIcon({ name, className }) {
  const Icon = iconMap[name] || Box;
  return <Icon className={className} />;
}

export default function SkillCard({ skill }) {
  const isComingSoon = skill.comingSoon;

  if (isComingSoon) {
    return (
      <div style={{
        padding: '16px',
        borderRadius: '8px',
        backgroundColor: '#0d0d14',
        border: '1px solid rgba(255,255,255,0.04)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          padding: '3px 8px',
          borderRadius: '4px',
          backgroundColor: 'rgba(168, 85, 247, 0.1)',
          border: '1px solid rgba(168, 85, 247, 0.2)',
          color: '#a855f7',
          fontSize: '10px',
          fontWeight: '500'
        }}>
          <Clock style={{ width: '10px', height: '10px' }} />
          Coming Soon
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: '12px',
          paddingRight: '60px'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '6px',
            backgroundColor: 'rgba(168, 85, 247, 0.05)',
            border: '1px solid rgba(168, 85, 247, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#71717a'
          }}>
            <SkillIcon name={skill.icon} style={{ width: '16px', height: '16px' }} />
          </div>
        </div>

        <h3 style={{
          fontSize: '15px',
          fontWeight: '600',
          color: '#52525b',
          marginBottom: '6px'
        }}>
          {skill.name}
        </h3>

        <p style={{
          color: '#3f3f46',
          fontSize: '12px',
          lineHeight: 1.45,
          marginBottom: '12px',
          flexGrow: 1
        }}>
          {skill.description}
        </p>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '4px',
          marginBottom: '10px'
        }}>
          {skill.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              style={{
                padding: '2px 6px',
                borderRadius: '3px',
                fontSize: '10px',
                backgroundColor: 'rgba(255,255,255,0.02)',
                color: '#52525b',
                border: '1px solid rgba(255,255,255,0.04)'
              }}
            >
              {tag}
            </span>
          ))}
        </div>

        <div style={{
          paddingTop: '10px',
          borderTop: '1px solid rgba(255,255,255,0.04)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '10px',
          color: '#3f3f46'
        }}>
          <span>{skill.author}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              {skill.stats?.views?.toLocaleString()}
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" x2="12" y1="15" y2="3" />
              </svg>
              {skill.stats?.downloads?.toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <a
      href={`/skills/${skill.id}`}
      style={{ display: 'block', textDecoration: 'none' }}
    >
      <div style={{
        padding: '16px',
        borderRadius: '8px',
        backgroundColor: '#12121a',
        border: '1px solid rgba(255,255,255,0.05)',
        transition: 'all 0.2s ease',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.2)';
        e.currentTarget.style.backgroundColor = '#13131f';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)';
        e.currentTarget.style.backgroundColor = '#12121a';
      }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: '12px'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '6px',
            backgroundColor: 'rgba(59, 130, 246, 0.08)',
            border: '1px solid rgba(59, 130, 246, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#60a5fa'
          }}>
            <SkillIcon name={skill.icon} style={{ width: '16px', height: '16px' }} />
          </div>
          <div style={{
            width: '24px',
            height: '24px',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: 0,
            transform: 'translateX(-2px)',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = '1';
            e.currentTarget.style.transform = 'translateX(0)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '0';
            e.currentTarget.style.transform = 'translateX(-2px)';
          }}
          >
            <ArrowRight style={{ width: '12px', height: '12px', color: '#a1a1aa' }} />
          </div>
        </div>

        <h3 style={{
          fontSize: '15px',
          fontWeight: '600',
          color: '#f4f4f5',
          marginBottom: '6px',
          transition: 'color 0.2s ease'
        }}
        onMouseEnter={(e) => e.target.style.color = '#60a5fa'}
        onMouseLeave={(e) => e.target.style.color = '#f4f4f5'}
        >
          {skill.name}
        </h3>

        <p style={{
          color: '#71717a',
          fontSize: '12px',
          lineHeight: 1.45,
          marginBottom: '12px',
          flexGrow: 1,
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical'
        }}>
          {skill.description}
        </p>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '4px',
          marginBottom: '10px'
        }}>
          {skill.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              style={{
                padding: '2px 6px',
                borderRadius: '3px',
                fontSize: '10px',
                backgroundColor: 'rgba(59, 130, 246, 0.05)',
                color: '#71717a',
                border: '1px solid rgba(59, 130, 246, 0.08)'
              }}
            >
              {tag}
            </span>
          ))}
        </div>

        <div style={{
          paddingTop: '10px',
          borderTop: '1px solid rgba(255,255,255,0.04)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '10px',
          color: '#52525b'
        }}>
          <span>{skill.author}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              {skill.stats?.views?.toLocaleString()}
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" x2="12" y1="15" y2="3" />
              </svg>
              {skill.stats?.downloads?.toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </a>
  );
}
