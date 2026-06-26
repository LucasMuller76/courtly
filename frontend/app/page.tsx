export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold text-foreground tracking-tight">
        🎾 Courtly
      </h1>
      <p className="text-muted-foreground text-lg">
        Secretária Virtual para Clubes de Padel
      </p>
      <div className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium">
        Frontend OK — API em localhost:8000
      </div>
    </main>
  );
}