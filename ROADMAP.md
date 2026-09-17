# BalanceManager roadmap

This roadmap describes **planned work**, not features of the current Python
application. The working Python desktop app and CLI remain available while a
Flutter/Dart replacement is built. We will not retire Python or move real data
without verifying the replacement and deciding how to carry that data across.

## Direction

- Build one Flutter client for Android and Windows first; target iOS later when
  macOS and Xcode are available for builds and testing.
- Keep SQLite as the active local database. Viewing and editing must not depend
  on network access.
- Add Supabase Auth and PostgreSQL synchronization after the local app is stable.
  Supabase is the planned cloud service; a custom Java server is not required.
- Learning Java remains an independent option, not a prerequisite for this app.
- Use JPY whole-yen amounts and `Asia/Tokyo` report boundaries. Store instants
  in UTC and generate record UUIDs offline.

## Phase 1 — Flutter and Dart foundation

- Set up Flutter on Windows and run a minimal app on Android and Windows.
- Learn the Dart and Flutter concepts needed for screens, state, and tests.
- Define domain models and local storage boundaries without depending on the
  network.
- Choose a maintained SQLite integration for Flutter during implementation.

Exit criterion: a small app launches on both target platforms and its local
data survives a restart.

## Phase 2 — Local ledger

- Create accounts with case-insensitively unique names, an opening balance and
  date, offline UUID, timestamps, and an archive state.
- Calculate current balances from opening amounts, real transactions,
  transfers, and signed adjustments rather than overwriting a stored balance.
- Require an active account and a positive whole-yen amount for every income
  and expense. Transfers use two different active accounts and do not change
  the all-account total.
- Allow negative account balances. Interpret entered dates in Japan time;
  reject future-dated real transactions.
- Archive accounts instead of deleting them. Keep archived accounts in history
  and totals, but exclude them from new-activity selectors.
- Soft-delete transactions. Keep descriptions and reasons for adjustments,
  deletion, and archiving optional.
- Prepare UUIDs, versions, timestamps, tombstones, and an outbox for eventual
  synchronization, without connecting to Supabase yet.

Exit criterion: balances remain correct after creating, editing, transferring,
adjusting, archiving, deleting, and restarting while offline.

## Phase 3 — Monthly reports

- Calculate each month using fixed `Asia/Tokyo` boundaries; past reports
  recalculate after corrections instead of being frozen snapshots.
- Show opening balance, closing balance (live balance in the current month),
  income, and expenses. Show adjustments and newly opened accounts as other
  balance changes. Transfers affect account balances but not income or expenses.
- Add previous/next month navigation, disable future months, and mark the
  current month **In progress**.
- Add a collapsed `Activity (N)` section containing transactions, transfers,
  adjustments, and opening-balance activity. Show transfers as
  `Source → Destination` and provide an edit action for real transactions.

Exit criterion: report tests cover empty months, Japan-time month/year
boundaries, transfers, adjustments, archived accounts, and past corrections.

## Phase 4 — Android and Windows stabilization

- Complete the local screens and verify offline editing on an Android device
  and Windows desktop.
- Test database persistence after app restart and recovery from interrupted
  operations.
- Use shared ledger fixtures to check the agreed balance and report rules.
- Keep the Python app available as a reference; do not assume its current
  database format is the Flutter format.

Exit criterion: both Flutter targets are useful without Supabase.

## Phase 5 — Supabase synchronization

- Create a Supabase project with PostgreSQL migrations, one invited Auth user,
  public registration disabled, and Row Level Security for owned records.
- Define version-controlled push/pull operations with mutation IDs, per-record
  versions, tombstones, an ordered change cursor, and idempotent retries.
- Save each local edit and its pending outbox entry atomically. Push pending
  changes before pulling cloud changes; never make the interface wait for a
  network request before showing local data.
- Show pending, offline, reauthentication-required, up-to-date, and conflict
  states. Preserve both versions of a conflict until the user chooses to keep
  local, keep cloud, or merge manually.
- Test authentication isolation, pagination, interrupted sync, retries,
  two-device conflicts, and operation while the cloud is unavailable.

Exit criterion: Android and Windows can work independently offline and later
converge safely through Supabase. Client applications use only the publishable
key; privileged keys stay out of the app.

## iOS release track

Flutter keeps iOS in scope, but an iOS release depends on access to macOS and
Xcode for building and testing. Test the same local ledger and synchronization
behavior on an iPhone before calling iOS support complete. Lack of a Mac must
not block Android and Windows progress.

## Deferred features

- Planned-payment reminders with optional amount, date, and account; reminders
  do not affect balances until converted into real expenses.
- Recurring reminders, global search, categories, charts, comparisons, and
  account breakdowns.
- A custom Java backend or replacement CLI, unless a future learning or product
  need justifies one.
