"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChartNoAxesCombined,
  ClipboardList,
  LayoutDashboard,
  Map,
  Menu,
  Settings
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const items = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/complaints", label: "Complaints", icon: ClipboardList },
  { href: "/admin/map", label: "Map View", icon: Map },
  { href: "/admin/analytics", label: "Analytics", icon: ChartNoAxesCombined },
  { href: "/admin/settings", label: "Settings", icon: Settings }
];

export function AdminSidebar({ mobile = false }: { mobile?: boolean }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  if (mobile) {
    return (
      <nav className="flex gap-2 overflow-x-auto border-b bg-card p-3 md:hidden">
        {items.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href || (item.href !== "/admin" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex shrink-0 items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium",
                active
                  ? "border-primary bg-primary/10 text-primary"
                  : "bg-background text-muted-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    );
  }

  return (
    <aside
      className={cn("hidden border-r bg-card transition-all md:block", collapsed ? "w-20" : "w-64")}
    >
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && <span className="font-bold">Mana Hyderabad</span>}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed((value) => !value)}
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </div>
      <nav className="space-y-1 p-3">
        {items.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href || (item.href !== "/admin" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground",
                active && "bg-primary/10 text-primary"
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
