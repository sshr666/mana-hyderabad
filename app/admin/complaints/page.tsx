"use client";

import {useEffect, useMemo, useState} from "react";
import {getAdminComplaints} from "@/lib/api-client";
import type {Complaint} from "@/lib/types";
import {ComplaintFilters, type ComplaintFilterState} from "@/components/admin/complaint-filters";
import {ComplaintTable} from "@/components/admin/complaint-table";
import {Button} from "@/components/ui/button";
import {Skeleton} from "@/components/ui/skeleton";

export default function AdminComplaintsPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [filters, setFilters] = useState<ComplaintFilterState>({
    search: "",
    category: "all",
    priority: "all",
    status: "all",
    locality: "all",
    language: "all",
    duplicate: "all"
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminComplaints().then((data) => {
      setComplaints(data);
      setLoading(false);
    });
  }, []);

  const filtered = useMemo(() => {
    const normalized = filters.search.toLowerCase();
    return complaints.filter((complaint) => {
      const matchesSearch = [complaint.id, complaint.landmark, complaint.subcategory, complaint.normalizedEnglishText]
        .join(" ")
        .toLowerCase()
        .includes(normalized);
      const matchesCategory = filters.category === "all" || complaint.category === filters.category;
      const matchesPriority = filters.priority === "all" || complaint.priority === filters.priority;
      const matchesStatus = filters.status === "all" || complaint.status === filters.status;
      const matchesLocality = filters.locality === "all" || complaint.landmark.toLowerCase().includes(filters.locality.toLowerCase());
      const matchesLanguage = filters.language === "all" || complaint.originalLanguage === filters.language;
      const hasDuplicate = Boolean(complaint.possibleDuplicateIds?.length);
      const matchesDuplicate = filters.duplicate === "all" || (filters.duplicate === "yes" ? hasDuplicate : !hasDuplicate);
      return matchesSearch && matchesCategory && matchesPriority && matchesStatus && matchesLocality && matchesLanguage && matchesDuplicate;
    });
  }, [complaints, filters]);

  const localities = useMemo(
    () => ["Kondapur", "Madhapur", "Gachibowli", "Ameerpet", "Kukatpally", "Charminar", "Jubilee Hills", "Hitech City", "Begumpet", "Secunderabad"],
    []
  );

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">Complaints</h1>
        <p className="text-muted-foreground">Review, filter, assign, and update civic complaints.</p>
      </header>
      <ComplaintFilters value={filters} onChange={setFilters} localities={localities} />
      {loading ? <Skeleton className="h-80 w-full" /> : <ComplaintTable complaints={filtered} />}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>Showing {filtered.length} of {complaints.length}</span>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setFilters({...filters, search: ""})}>Clear Search</Button>
          <Button variant="outline" size="sm" onClick={() => setFilters({search: "", category: "all", priority: "all", status: "all", locality: "all", language: "all", duplicate: "all"})}>Reset Filters</Button>
        </div>
      </div>
    </div>
  );
}
