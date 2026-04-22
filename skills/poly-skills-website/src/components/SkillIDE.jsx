import React, { useState, useEffect, useRef } from 'react';
import { 
  Folder, 
  FileText, 
  ChevronRight, 
  ChevronDown, 
  FileCode, 
  Menu,
  X,
  Github,
  Download,
  Eye,
  Copy,
  Check,
  ChevronLeft,
  ExternalLink,
  ClipboardCopy,
  Archive,
  Terminal,
  Hash,
  Box
} from 'lucide-react';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import python from 'react-syntax-highlighter/dist/cjs/languages/prism/python';
import json from 'react-syntax-highlighter/dist/cjs/languages/prism/json';
import bash from 'react-syntax-highlighter/dist/cjs/languages/prism/bash';
import markdown from 'react-syntax-highlighter/dist/cjs/languages/prism/markdown';
import vscDarkPlus from 'react-syntax-highlighter/dist/cjs/styles/prism/vsc-dark-plus';
import SkillIcon from './SkillIcon';

SyntaxHighlighter.registerLanguage('python', python.default || python);
SyntaxHighlighter.registerLanguage('json', json.default || json);
SyntaxHighlighter.registerLanguage('bash', bash.default || bash);
SyntaxHighlighter.registerLanguage('md', markdown.default || markdown);

const Dropdown = ({ trigger, items, onSelect, align = 'left' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
      {isOpen && (
        <div className={`absolute ${align === 'right' ? 'right-0' : 'left-0'} top-full mt-2 w-52 bg-[#111] border border-[#333] rounded-lg shadow-xl z-50 py-1.5`}>
          {items.map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                onSelect(item.action);
                setIsOpen(false);
              }}
              disabled={item.loading}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:bg-[#222] hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {item.loading ? (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="text-gray-500">{item.icon}</span>
              )}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

const InstallDropdown = ({ skill }) => {
  const [downloading, setDownloading] = useState(null);
  const [showToast, setShowToast] = useState(null);

  const downloadFile = async (filename, content, isMarkdown = false) => {
    setDownloading(filename);
    try {
      const blob = new Blob([content], { type: isMarkdown ? 'text/markdown' : 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setShowToast(`${filename} downloaded!`);
    } catch (error) {
      setShowToast('Download failed');
    }
    setDownloading(null);
    setTimeout(() => setShowToast(null), 3000);
  };

  const downloadFullRepo = () => {
    setDownloading('full');
    window.open(`${skill.repository}/archive/refs/heads/main.zip`, '_blank');
    setShowToast('Downloading repository...');
    setTimeout(() => setShowToast(null), 3000);
  };

  const installItems = [
    {
      icon: <FileText className="w-4 h-4" />,
      label: 'Download SKILL.md',
      action: 'skillmd',
      loading: downloading === 'SKILL.md'
    },
    {
      icon: <Archive className="w-4 h-4" />,
      label: 'Download Full Directory',
      action: 'full',
      loading: downloading === 'full'
    }
  ];

  return (
    <>
      {showToast && (
        <div className="fixed top-20 right-6 z-50 bg-[#111] text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 border border-[#333]">
          <div className="w-5 h-5 bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/20">
            <Check className="w-3 h-3 text-green-500" />
          </div>
          {showToast}
        </div>
      )}
      <Dropdown
        trigger={
          <button className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-white text-black font-medium hover:bg-gray-100 transition-colors cursor-pointer text-sm">
            <Download className="w-4 h-4" />
            Download
            <ChevronDown className="w-4 h-4 opacity-50" />
          </button>
        }
        items={installItems}
        onSelect={(type) => {
          if (type === 'skillmd') {
             const skillMdContent = skill.files?.['SKILL.md']?.content; 
             if (skillMdContent) {
                 downloadFile('SKILL.md', skillMdContent, true);
             } else {
                 fetch(skill.repository.replace('github.com', 'raw.githubusercontent.com') + '/main/SKILL.md')
                    .then(r => r.text())
                    .then(t => downloadFile('SKILL.md', t, true));
             }
          } else {
            downloadFullRepo();
          }
        }}
      />
    </>
  );
};

const AICopyDropdown = ({ content, selectedFile }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!content) return null;

  return (
    <button 
      onClick={handleCopy}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#222] hover:bg-[#333] text-gray-300 font-medium border border-[#333] transition-all text-xs cursor-pointer"
    >
      {copied ? (
        <>
          <Check className="w-3.5 h-3.5 text-green-500" />
          Copied
        </>
      ) : (
        <>
          <ClipboardCopy className="w-3.5 h-3.5" />
          Copy
        </>
      )}
    </button>
  );
};

const FileIcon = ({ name }) => {
  if (name.endsWith('.md')) return <FileText className="w-4 h-4 text-blue-400" />;
  if (name.endsWith('.py')) return <FileCode className="w-4 h-4 text-yellow-400" />;
  if (name.endsWith('.json')) return <FileCode className="w-4 h-4 text-green-400" />;
  return <FileText className="w-4 h-4 text-gray-500" />;
};

const useSkillContent = (skill) => {
  const [files, setFiles] = useState(skill.files || {});
  const [fetching, setFetching] = useState({});

  const fetchFile = async (path) => {
    if (files[path]) return;
    if (fetching[path]) return;

    setFetching(prev => ({ ...prev, [path]: true }));
    try {
      const url = skill.repository
        .replace('github.com', 'raw.githubusercontent.com')
        .replace('/blob/', '/')
        + `/main/${path}`;

      const response = await fetch(url);
      if (response.ok) {
        const content = await response.text();
        setFiles(prev => ({
          ...prev,
          [path]: { content, path }
        }));
      }
    } catch (err) {
      console.error(`Error fetching ${path}:`, err);
    } finally {
      setFetching(prev => ({ ...prev, [path]: false }));
    }
  };

  return { files, fetching, fetchFile };
};

const FileTreeNode = ({ node, level = 0, onSelect, selectedFile, path = '' }) => {
  const [isOpen, setIsOpen] = useState(level === 0 || (path && selectedFile?.path?.startsWith(path)));
  const currentPath = node.path || (path ? `${path}/${node.name}` : node.name);
  const isSelected = selectedFile?.path === currentPath;

  if (node.type === 'folder') {
    return (
      <div className="mb-0.5">
        <div 
          className="flex items-center gap-1.5 py-1.5 px-3 hover:bg-[#1a1a1a] cursor-pointer text-gray-500 hover:text-gray-300 transition-colors select-none text-sm group rounded-md mx-2"
          style={{ paddingLeft: `${level * 12 + 12}px` }}
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-gray-600 group-hover:text-gray-400 transition-colors" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-gray-600 group-hover:text-gray-400 transition-colors" />
          )}
          <Folder className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" />
          <span className="font-medium text-gray-400 group-hover:text-gray-200">{node.name}</span>
        </div>
        {isOpen && node.children && (
          <div className="border-l border-[#222] ml-[22px]">
             {node.children.map((child) => (
              <FileTreeNode 
                key={child.path || child.name} 
                node={child} 
                level={level + 1} 
                onSelect={onSelect}
                selectedFile={selectedFile}
                path={currentPath}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div 
      className={`
        flex items-center gap-2 py-1.5 px-3 cursor-pointer text-sm transition-all duration-150 rounded-md mx-2 mb-0.5
        ${isSelected 
          ? 'bg-[#1a1a1a] text-white border border-[#333]' 
          : 'border border-transparent text-gray-500 hover:bg-[#111] hover:text-gray-300'
        }
      `}
      style={{ paddingLeft: `${level * 12 + 12}px` }}
      onClick={() => onSelect(node)}
    >
      <FileIcon name={node.name} />
      <span>{node.name}</span>
    </div>
  );
};

const CodeViewer = ({ content, language, isLoading }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="rounded-xl overflow-hidden border border-[#222] bg-[#0a0a0a] p-8 flex items-center justify-center">
        <div className="flex items-center gap-3 text-gray-400">
          <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl overflow-hidden border border-[#222] bg-[#0a0a0a] my-8 group">
      <div className="flex items-center justify-between px-4 py-2 bg-[#111] border-b border-[#222]">
        <div className="flex items-center gap-2">
           <Terminal className="w-4 h-4 text-gray-500" />
           <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">{language}</span>
        </div>
        <button 
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-[#222] transition-colors text-xs text-gray-400 hover:text-white cursor-pointer"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <div className="text-sm font-mono leading-relaxed">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          customStyle={{ margin: 0, padding: '1.5rem', background: 'transparent' }}
          showLineNumbers={true}
          lineNumberStyle={{ minWidth: '2.5em', paddingRight: '1em', color: '#4b5563', textAlign: 'right' }}
        >
          {content}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

const HeaderCard = ({ skill }) => {
  return (
    <div className="mb-8 p-1">
      <div className="rounded-xl p-8 bg-[#0a0a0a] border border-[#222]">
        <div className="flex flex-col lg:flex-row gap-6 items-start">
          <div className="w-16 h-16 rounded-xl bg-[#111] border border-[#222] flex items-center justify-center text-white flex-shrink-0">
            <SkillIcon name={skill.icon} className="w-8 h-8" />
          </div>
          
          <div className="flex-1 min-w-0 w-full">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white tracking-tight">{skill.name}</h1>
              <span className="px-2 py-0.5 rounded-full bg-[#1a1a1a] border border-[#333] text-xs font-medium text-gray-400">
                v1.0.0
              </span>
            </div>
            
            <p className="text-lg text-gray-400 leading-relaxed mb-6 max-w-2xl">
              {skill.description}
            </p>
            
            <div className="flex flex-wrap items-center gap-3">
              <InstallDropdown skill={skill} />
              <a 
                href={skill.repository}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-[#111] hover:bg-[#222] text-gray-300 font-medium border border-[#333] transition-all cursor-pointer text-sm"
              >
                <Github className="w-4 h-4" />
                View Source
              </a>
            </div>
          </div>

          <div className="hidden lg:flex gap-8 px-6 py-4 rounded-xl bg-[#111] border border-[#222]">
             <div className="text-center">
               <div className="text-2xl font-bold text-white mb-1">{skill.stats?.views?.toLocaleString()}</div>
               <div className="text-xs text-gray-500 uppercase tracking-wider font-medium">Views</div>
             </div>
             <div className="w-px bg-[#222]"></div>
             <div className="text-center">
               <div className="text-2xl font-bold text-white mb-1">{skill.stats?.downloads?.toLocaleString()}</div>
               <div className="text-xs text-gray-500 uppercase tracking-wider font-medium">Installs</div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function SkillIDE({ skill }) {
  const { files, fetching, fetchFile } = useSkillContent(skill);
  const findFile = (nodes, name) => {
    for (const node of nodes) {
      if (node.name === name) return { ...node, path: node.path || name };
      if (node.children) {
        const found = findFile(node.children, name);
        if (found) return found;
      }
    }
    return null;
  };

  const initialFile = findFile(skill.fileTree, 'SKILL.md') || skill.fileTree[0];
  const [selectedFile, setSelectedFile] = useState(initialFile);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    if (selectedFile) {
      fetchFile(selectedFile.path);
    }
  }, [selectedFile]);

  const getFileContent = (file) => {
    if (!file) return '';
    const fileData = files[file.path];
    if (fileData) return fileData.content;
    return null;
  };

  const content = getFileContent(selectedFile);
  const extension = selectedFile?.name.split('.').pop() || '';
  const language = extension === 'py' ? 'python' : extension === 'json' ? 'json' : extension === 'md' ? 'md' : 'bash';
  const isLoadingFile = content === null && fetching[selectedFile?.path];

  // We are using a simpler layout structure that avoids fixed/calc heights
  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-[#000]">
      
      {/* Mobile Header Bar */}
      <div className="lg:hidden flex items-center justify-between p-4 border-b border-[#222] bg-[#050505] sticky top-0 z-30">
        <div className="flex items-center gap-2 text-sm font-medium text-white">
          <SkillIcon name={skill.icon} className="w-5 h-5 text-gray-400" />
          <span className="truncate max-w-[200px]">{skill.name}</span>
        </div>
        <button 
          className="p-2 rounded-md bg-[#1a1a1a] text-white border border-[#333]"
          onClick={() => setIsSidebarOpen(true)}
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Sidebar - File Explorer */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-[#050505] border-r border-[#222] transform transition-transform duration-200 ease-out flex flex-col
        lg:static lg:translate-x-0 lg:h-auto lg:min-h-screen
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-14 flex items-center justify-between px-5 border-b border-[#222] bg-[#050505] flex-shrink-0">
          <span className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
            <Box className="w-4 h-4" />
            Explorer
          </span>
          <button 
            className="lg:hidden text-gray-500"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X size={18} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto py-3 px-2 custom-scrollbar">
          {skill.fileTree.map((node) => (
            <FileTreeNode 
              key={node.name} 
              node={node} 
              onSelect={(file) => {
                setSelectedFile(file);
                setIsSidebarOpen(false);
              }}
              selectedFile={selectedFile}
            />
          ))}
        </div>
        
        <div className="p-4 border-t border-[#222] bg-[#050505] flex-shrink-0">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 rounded-md bg-[#1a1a1a] border border-[#333] text-gray-400 flex items-center justify-center text-xs font-bold">
               {skill.author?.substring(0,2).toUpperCase() || 'AU'}
             </div>
             <div className="flex-1 min-w-0">
               <div className="text-sm font-medium text-white truncate">{skill.author || 'Author'}</div>
               <a href={skill.repository} target="_blank" rel="noopener noreferrer" className="text-xs text-gray-500 hover:text-gray-300 truncate block">
                 @GitHub
               </a>
             </div>
          </div>
        </div>
      </div>

      {/* Backdrop for mobile */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 relative bg-[#000]">
        
        {/* Breadcrumb Header - Sticky on Desktop only */}
        <div className="h-14 border-b border-[#222] flex items-center justify-between px-4 sm:px-6 bg-[#000]/95 sticky top-0 z-20 backdrop-blur-sm flex-shrink-0">
          <div className="flex items-center gap-2 text-sm overflow-hidden whitespace-nowrap">
            <span className="text-gray-500 hidden sm:inline">Current File:</span>
            <span className="text-white flex items-center gap-2 font-medium">
              <FileIcon name={selectedFile?.name || ''} />
              <span className="truncate max-w-[200px] sm:max-w-[400px]">{selectedFile?.name}</span>
            </span>
          </div>
          
          <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
            <a 
              href={`${skill.repository}/blob/main/${selectedFile?.path}`} 
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-500 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer font-medium"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Open in GitHub</span>
            </a>
            {content && <AICopyDropdown content={content} selectedFile={selectedFile} />}
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 p-4 sm:p-8">
          <div className="max-w-5xl mx-auto">
            {selectedFile?.name === 'SKILL.md' && (
              <HeaderCard skill={skill} />
            )}

            <div className="min-h-[500px]">
              {isLoadingFile ? (
                 <div className="flex items-center justify-center py-20">
                   <div className="flex items-center gap-3 text-gray-500">
                     <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                     Loading content...
                   </div>
                 </div>
               ) : content ? (
                 <div className="animate-in fade-in duration-300">
                   <CodeViewer content={content} language={language} />
                 </div>
               ) : (
                 <div className="text-center py-20 text-gray-500 border border-dashed border-[#222] rounded-xl">
                   Unable to load file content.
                 </div>
               )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
