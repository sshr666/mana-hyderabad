"use client";

import {Search} from "lucide-react";
import type {ComplaintCategory, ComplaintPriority, ComplaintStatus, SupportedLanguage} from "@/lib/types";
import {Input} from "@/components/ui/input";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";

export interface ComplaintFilterState {
  search: string;
  category: ComplaintCategory | "all";
  priority: ComplaintPriority | "all";
  status: ComplaintStatus | "all";
  locality: string;
  language: SupportedLanguage | "all";
  duplicate: "all" | "yes" | "no";
}

interface ComplaintFiltersProps {
  value: ComplaintFilterState;
  onChange: (value: ComplaintFilterState) => void;
  localities: string[];
}

export function ComplaintFilters({value, onChange, localities}: ComplaintFiltersProps) {
  const update = (next: Partial<ComplaintFilterState>) => onChange({...value, ...next});

  return (
    <div className="grid gap-3 rounded-xl border bg-card p-4 md:grid-cols-4 xl:grid-cols-8">
      <div className="relative md:col-span-2">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Search complaints"
          value={value.search}
          onChange={(event) => update({search: event.target.value})}
        />
      </div>
      <Select value={value.category} onValueChange={(category) => update({category: category as ComplaintFilterState["category"]})}>
        <SelectTrigger><SelectValue placeholder="Category" /></SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All categories</SelectItem>
          {["SANITATION", "DRAINAGE", "WATERLOGGING", "ROADS", "STREET_LIGHTS", "WATER_SUPPLY", "TRAFFIC", "OTHER"].map((item) => (
            <SelectItem key={item} value={item}>{item.replaceAll("_", " ")}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select value={value.priority} onValueChange={(priority) => update({priority: priority as ComplaintFilterState["priority"]})}>
        <SelectTrigger><SelectValue placeholder="Priority" /></SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All priorities</SelectItem>
          {["LOW", "MEDIUM", "HIGH", "EMERGENCY"].map((item) => (
            <SelectItem key={item} value={item}>{item}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select value={value.status} onValueChange={(status) => update({status: status as ComplaintFilterState["status"]})}>
        <SelectTrigger><SelectValue placeholder="Status" /></SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All statuses</SelectItem>
          {["SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED"].map((item) => (
            <SelectItem key={item} value={item}>{item.replaceAll("_", " ")}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select value={value.locality} onValueChange={(locality) => update({locality})}>
        <SelectTrigger><SelectValue placeholder="Locality" /></SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All localities</SelectItem>
          {localities.map((locality) => (
            <SelectItem key={locality} value={locality}>{locality}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select value={value.language} onValueChange={(language) => update({language: language as ComplaintFilterState["language"]})}>
        <SelectTrigger><SelectValue placeholder="Language" /></SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All languages</SelectItem>
          <SelectItem value="en">English</SelectItem>
          <SelectItem value="te">Telugu</SelectItem>
          <SelectItem value="hi">Hindi</SelectItem>
          <SelectItem value="ur">Urdu</SelectItem>
        </SelectContent>
      </Select>
      <Select value={value.duplicate} onValueChange={(duplicate) => update({duplicate: duplicate as ComplaintFilterState["duplicate"]})}>
        <SelectTrigger>
          <SelectValue placeholder="Duplicate" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All</SelectItem>
          <SelectItem value="yes">Possible duplicate</SelectItem>
          <SelectItem value="no">Not flagged</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
