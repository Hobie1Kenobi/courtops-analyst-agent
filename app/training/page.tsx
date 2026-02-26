"use client";

import { useState } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  BookOpen,
  Code,
  Database,
  HelpCircle,
  FileText,
  TestTube,
  UserCheck,
  CheckCircle2,
  Circle,
  ChevronRight,
  Zap,
  Target,
  Brain,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

/* ------------------------------------------------------------------ */
/*  Mock data                                                          */
/* ------------------------------------------------------------------ */

const modes = [
  { id: "teach", label: "Teach Me", icon: BookOpen },
  { id: "technical", label: "Technical Detail", icon: Code },
  { id: "sql", label: "SQL", icon: Database },
  { id: "ask-why", label: "Ask Why", icon: HelpCircle },
  { id: "docs", label: "Documentation", icon: FileText },
  { id: "testing", label: "Testing", icon: TestTube },
  { id: "interview", label: "Interview Prep", icon: UserCheck },
];

interface Scenario {
  id: string;
  title: string;
  description: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  modules: number;
  completed: number;
}

const scenarios: Scenario[] = [
  {
    id: "sla-management",
    title: "SLA Management & Compliance",
    description: "Learn SLA tracking, escalation workflows, and compliance reporting.",
    difficulty: "Beginner",
    modules: 6,
    completed: 4,
  },
  {
    id: "case-lifecycle",
    title: "Case Lifecycle Management",
    description: "Understand case filing, disposition, aging analysis, and FTA workflows.",
    difficulty: "Intermediate",
    modules: 8,
    completed: 3,
  },
  {
    id: "revenue-risk",
    title: "Revenue-at-Risk Analysis",
    description: "Identify and analyze revenue leakage from FTA cases and uncollected fines.",
    difficulty: "Advanced",
    modules: 5,
    completed: 1,
  },
  {
    id: "audit-security",
    title: "Audit & Security Operations",
    description: "Scan for anomalies, review audit trails, and handle security incidents.",
    difficulty: "Intermediate",
    modules: 7,
    completed: 0,
  },
  {
    id: "patch-management",
    title: "Patch & Change Management",
    description: "Manage application patches, verification workflows, and change requests.",
    difficulty: "Beginner",
    modules: 4,
    completed: 4,
  },
];

const difficultyColors = {
  Beginner: "success" as const,
  Intermediate: "warning" as const,
  Advanced: "danger" as const,
};

const skills = [
  { name: "Data Analysis", level: 72 },
  { name: "SQL Queries", level: 45 },
  { name: "SLA Compliance", level: 88 },
  { name: "Audit Review", level: 30 },
  { name: "Report Generation", level: 65 },
];

const workQueue = [
  { id: 1, task: "Review SLA escalation policy", done: true },
  { id: 2, task: "Run compliance check query", done: true },
  { id: 3, task: "Analyze overdue ticket patterns", done: false },
  { id: 4, task: "Generate SLA exception report", done: false },
  { id: 5, task: "Document findings and recommendations", done: false },
];

const trainingFeed = [
  {
    time: "10:32 AM",
    message: "Completed module: Understanding SLA Tiers",
    type: "success" as const,
  },
  {
    time: "10:28 AM",
    message: "Ran SQL query: SELECT tickets WHERE sla_met = false",
    type: "info" as const,
  },
  {
    time: "10:25 AM",
    message: "Scenario started: SLA Management & Compliance",
    type: "default" as const,
  },
  {
    time: "10:22 AM",
    message: "Skill assessment updated: SLA Compliance +5%",
    type: "success" as const,
  },
];

/* ------------------------------------------------------------------ */

export default function TrainingPage() {
  const [activeMode, setActiveMode] = useState("teach");
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(
    scenarios[0]
  );
  const [isRunning, setIsRunning] = useState(true);

  return (
    <div className="space-y-6">
      {/* Skills Progress Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              <span className="text-sm font-semibold text-foreground">
                Skills Progress
              </span>
            </div>
            {skills.map((skill) => (
              <div key={skill.name} className="flex-1 min-w-[120px]">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">{skill.name}</span>
                  <span className="font-semibold text-foreground">
                    {skill.level}%
                  </span>
                </div>
                <Progress
                  value={skill.level}
                  variant={
                    skill.level >= 80
                      ? "success"
                      : skill.level >= 50
                      ? "primary"
                      : "warning"
                  }
                  size="sm"
                  className="mt-1"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Left Panel: Scenarios + Work Queue */}
        <div className="space-y-4 lg:col-span-1">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Scenarios</CardTitle>
              <Badge variant="muted">{scenarios.length}</Badge>
            </CardHeader>
            <CardContent className="space-y-2 p-3">
              {scenarios.map((scenario) => {
                const isActive = activeScenario?.id === scenario.id;
                const pct = Math.round(
                  (scenario.completed / scenario.modules) * 100
                );

                return (
                  <button
                    key={scenario.id}
                    onClick={() => setActiveScenario(scenario)}
                    className={`w-full rounded-md border p-3 text-left transition-colors ${
                      isActive
                        ? "border-primary bg-primary/5"
                        : "border-border hover:bg-muted/50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-foreground leading-snug">
                        {scenario.title}
                      </p>
                      <ChevronRight
                        className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${
                          isActive
                            ? "text-primary"
                            : "text-muted-foreground"
                        }`}
                      />
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                      <Badge variant={difficultyColors[scenario.difficulty]}>
                        {scenario.difficulty}
                      </Badge>
                      <span className="text-[11px] text-muted-foreground">
                        {scenario.completed}/{scenario.modules} modules
                      </span>
                    </div>
                    <Progress
                      value={pct}
                      variant={pct === 100 ? "success" : "primary"}
                      size="sm"
                      className="mt-2"
                    />
                  </button>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Work Queue</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5 p-3">
              {workQueue.map((item) => (
                <div
                  key={item.id}
                  className="flex items-start gap-2 rounded-md px-2 py-1.5"
                >
                  {item.done ? (
                    <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success" />
                  ) : (
                    <Circle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  )}
                  <span
                    className={`text-xs ${
                      item.done
                        ? "text-muted-foreground line-through"
                        : "text-foreground"
                    }`}
                  >
                    {item.task}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Center Panel: Content Area */}
        <div className="space-y-4 lg:col-span-3">
          {/* Scenario Header + Controls */}
          {activeScenario && (
            <Card>
              <CardContent className="flex flex-wrap items-center justify-between gap-4 p-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Target className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">
                      {activeScenario.title}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {activeScenario.description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant={isRunning ? "outline" : "primary"}
                    size="sm"
                    onClick={() => setIsRunning(!isRunning)}
                  >
                    {isRunning ? (
                      <>
                        <Pause className="mr-1 h-3 w-3" />
                        Pause
                      </>
                    ) : (
                      <>
                        <Play className="mr-1 h-3 w-3" />
                        Resume
                      </>
                    )}
                  </Button>
                  <Button variant="ghost" size="sm">
                    <RotateCcw className="mr-1 h-3 w-3" />
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Mode Tabs */}
          <Card>
            <CardContent className="p-0">
              <div className="flex overflow-x-auto border-b">
                {modes.map((mode) => {
                  const Icon = mode.icon;
                  const isActive = activeMode === mode.id;
                  return (
                    <button
                      key={mode.id}
                      onClick={() => setActiveMode(mode.id)}
                      className={`flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-3 text-xs font-medium transition-colors ${
                        isActive
                          ? "border-primary text-primary"
                          : "border-transparent text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      {mode.label}
                    </button>
                  );
                })}
              </div>
              <div className="p-6">
                <div className="rounded-lg bg-muted/30 p-8 text-center">
                  <Zap className="mx-auto h-8 w-8 text-muted-foreground" />
                  <h4 className="mt-3 text-sm font-semibold text-foreground">
                    {modes.find((m) => m.id === activeMode)?.label} Mode
                  </h4>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Training content will appear here when connected to the
                    backend. Select a scenario and mode to begin learning.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Training Feed */}
          <Card>
            <CardHeader>
              <CardTitle>Activity Feed</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ul className="divide-y">
                {trainingFeed.map((item, i) => (
                  <li key={i} className="flex items-center gap-3 px-4 py-2.5">
                    <Badge variant={item.type}>{item.time}</Badge>
                    <span className="text-sm text-foreground">
                      {item.message}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
