import React from 'react';

const Hero = () => {
  return (
    <div style={{
      backgroundColor: '#0a0a0a',
      borderBottom: '1px solid #1f1f1f'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '120px 32px 100px'
      }}>
        {/* Main Content */}
        <div style={{
          maxWidth: '800px',
          margin: '0 auto',
          textAlign: 'center'
        }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '100px',
            backgroundColor: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            fontSize: '13px',
            color: '#a0a0a0',
            fontWeight: '500',
            marginBottom: '32px'
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            Open Source MCP Skills
          </div>

          {/* Title */}
          <h1 style={{
            fontSize: '64px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '24px',
            letterSpacing: '-0.03em',
            lineHeight: 1.1
          }}>
            Polymarket Skills for AI Agents
          </h1>

          {/* Description */}
          <p style={{
            fontSize: '20px',
            color: '#a0a0a0',
            maxWidth: '640px',
            margin: '0 auto 48px',
            lineHeight: 1.6
          }}>
            Add Polymarket capabilities to your AI agent. Search markets, execute trades, and track portfolios with ready-to-use skills.
          </p>

          {/* Buttons */}
          <div style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
            flexWrap: 'wrap',
            marginBottom: '80px'
          }}>
            <a
              href="#skills"
              style={{
                padding: '14px 32px',
                borderRadius: '8px',
                backgroundColor: '#ffffff',
                color: '#000000',
                fontSize: '15px',
                fontWeight: '600',
                textDecoration: 'none',
                transition: 'all 0.2s',
                display: 'inline-block'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#e6e6e6';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#ffffff';
              }}
            >
              Browse Skills
            </a>

            <a
              href="https://github.com/DevAgarwal2/poly-skills-website"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: '14px 32px',
                borderRadius: '8px',
                backgroundColor: 'transparent',
                border: '1px solid #2f2f2f',
                color: '#ffffff',
                fontSize: '15px',
                fontWeight: '600',
                textDecoration: 'none',
                transition: 'all 0.2s',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'rgba(255,255,255,0.05)';
                e.target.style.borderColor = '#3f3f3f';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.borderColor = '#2f2f2f';
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </a>
          </div>

          {/* Features */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '24px',
            maxWidth: '1000px',
            margin: '0 auto 100px',
            textAlign: 'left'
          }}>
            <div style={{
              padding: '28px',
              borderRadius: '12px',
              backgroundColor: '#141414',
              border: '1px solid #1f1f1f'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: 'rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px'
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <path d="M21 21l-4.3-4.3" />
                </svg>
              </div>
              <h3 style={{
                fontSize: '17px',
                fontWeight: '600',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                Market Intelligence
              </h3>
              <p style={{
                fontSize: '15px',
                color: '#a0a0a0',
                lineHeight: 1.6,
                margin: 0
              }}>
                Search and analyze prediction markets. Get real-time prices, event data, and market trends.
              </p>
            </div>

            <div style={{
              padding: '28px',
              borderRadius: '12px',
              backgroundColor: '#141414',
              border: '1px solid #1f1f1f'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: 'rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px'
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
              </div>
              <h3 style={{
                fontSize: '17px',
                fontWeight: '600',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                Trading Automation
              </h3>
              <p style={{
                fontSize: '15px',
                color: '#a0a0a0',
                lineHeight: 1.6,
                margin: 0
              }}>
                Execute trades and manage positions on Polymarket CLOB. Automate your trading strategies.
              </p>
            </div>

            <div style={{
              padding: '28px',
              borderRadius: '12px',
              backgroundColor: '#141414',
              border: '1px solid #1f1f1f'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: 'rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px'
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2">
                  <path d="M3 3v18h18" />
                  <path d="M18 17V9" />
                  <path d="M13 17V5" />
                  <path d="M8 17v-3" />
                </svg>
              </div>
              <h3 style={{
                fontSize: '17px',
                fontWeight: '600',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                Portfolio Analytics
              </h3>
              <p style={{
                fontSize: '15px',
                color: '#a0a0a0',
                lineHeight: 1.6,
                margin: 0
              }}>
                Track P&L, view trading history, and monitor your positions across all markets.
              </p>
            </div>
          </div>

          {/* Stats */}
          <div style={{
            display: 'flex',
            gap: '80px',
            justifyContent: 'center',
            flexWrap: 'wrap',
            paddingTop: '60px',
            borderTop: '1px solid #1f1f1f'
          }}>
            <div>
              <div style={{
                fontSize: '36px',
                fontWeight: '700',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                3
              </div>
              <div style={{
                fontSize: '14px',
                color: '#6f6f6f'
              }}>
                Skills Available
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '36px',
                fontWeight: '700',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                $3B+
              </div>
              <div style={{
                fontSize: '14px',
                color: '#6f6f6f'
              }}>
                Platform Volume
              </div>
            </div>

            <div>
              <div style={{
                fontSize: '36px',
                fontWeight: '700',
                color: '#ffffff',
                marginBottom: '8px'
              }}>
                MIT
              </div>
              <div style={{
                fontSize: '14px',
                color: '#6f6f6f'
              }}>
                Open Source
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
