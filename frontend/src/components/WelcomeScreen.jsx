import React from 'react'
import { BarChart3, Calculator, Table, Wand2 } from 'lucide-react'

const quickActions = [
  {
    icon: <BarChart3 size={20} />,
    title: 'Sales Dashboard',
    desc: 'Interactive sales dashboard with charts and KPIs',
    prompt: 'Create a professional sales dashboard with monthly revenue chart, top products table, KPI cards for total sales/growth/avg order value, and conditional formatting for targets',
  },
  {
    icon: <Calculator size={20} />,
    title: 'Financial Calculator',
    desc: 'Budget tracker or loan calculator with formulas',
    prompt: 'Create a personal budget tracker with income/expense categories, monthly tracking, running totals, variance analysis, and a pie chart showing expense breakdown',
  },
  {
    icon: <Table size={20} />,
    title: 'Project Tracker',
    desc: 'Project management spreadsheet with status tracking',
    prompt: 'Create a project task tracker with columns for task name, assignee, priority, status, start date, due date, % complete, and a Gantt-chart-style timeline. Include data validation dropdowns for priority and status.',
  },
  {
    icon: <Wand2 size={20} />,
    title: 'Custom Macro',
    desc: 'VBA automation for repetitive tasks',
    prompt: 'Create a VBA macro that automates data cleaning: removes duplicates, trims whitespace, standardizes date formats, highlights empty cells, and generates a summary report on a new sheet',
  },
]

export default function WelcomeScreen({ onAction }) {
  return (
    <div className="welcome">
      <div className="welcome-icon">X</div>
      <h2>Excel Master Worker</h2>
      <p>
        Describe the Excel file, dashboard, or macro you need and I'll create it for you.
        Upload existing files to modify them, or ask for step-by-step guidance.
      </p>
      <div className="quick-actions">
        {quickActions.map((action, i) => (
          <div key={i} className="quick-action" onClick={() => onAction(action.prompt)}>
            <h4>{action.icon} {action.title}</h4>
            <p>{action.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
