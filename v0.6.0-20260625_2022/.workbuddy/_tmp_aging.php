    private function agingByModel($query, string $dateCol): array
    {
        $today = now()->startOfDay();
        $isSupplier = str_contains(get_class($query->getModel()), 'SupplierPayable');
        $items = $query->whereIn('status', ['pending', 'partial', 'overdue'])->get();
