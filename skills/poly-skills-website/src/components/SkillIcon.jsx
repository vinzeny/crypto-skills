import React from 'react';
import { BarChart3, Users, Layout, Database, Activity, Globe, Zap, Search, Box } from 'lucide-react';

const iconMap = {
  BarChart3,
  Users,
  Layout,
  Database,
  Activity,
  Globe,
  Zap,
  Search,
  Box
};

export default function SkillIcon({ name, className }) {
  const Icon = iconMap[name] || Box;
  return <Icon className={className} />;
}
