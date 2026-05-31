import { AdminSidebar } from "@/components/admin/admin-sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-secondary/30">
      <AdminSidebar />
      <main className="min-w-0 flex-1">
        <AdminSidebar mobile />
        {children}
      </main>
    </div>
  );
}
