export default function Header() {
  return (
    <header className="px-5 py-2.5 border-b surface">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md flex items-center justify-center brand-icon">
            <span className="font-bold text-xs">FO</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold brand-title">Family Office Intelligence</h1>
            <p className="text-[11px] brand-sub">200 offices &middot; 45 fields &middot; 6 regions</p>
          </div>
        </div>
        <span className="text-[11px] px-2 py-0.5 rounded font-medium border status-badge">
          Connected
        </span>
      </div>
    </header>
  );
}
