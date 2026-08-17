// queen_dashboard.ts — ANCHA Throne Room viewer
// Setup: npm install @supabase/supabase-js && npx tsc queen_dashboard.ts
import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabase: SupabaseClient = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!
);

async function throneRoom(): Promise<void> {
  const { data, error } = await supabase
    .from("findings")
    .select("*")
    .order("ts", { ascending: false })
    .limit(25);
  if (error) { console.error("vault unreachable:", error.message); return; }
  console.log("=== ANCHA THRONE ROOM — latest findings ===");
  for (const f of data ?? []) {
    console.log(`[${f.domain}] ${f.tool} -> ${f.target} : ${JSON.stringify(f.data)}`);
  }
}

throneRoom();
