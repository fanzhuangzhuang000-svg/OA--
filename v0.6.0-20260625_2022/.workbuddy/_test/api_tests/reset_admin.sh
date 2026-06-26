#!/bin/bash
cd /var/www/oa-api
sudo -u www-data php -r "
require 'vendor/autoload.php';
\$app = require 'bootstrap/app.php';
\$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
\$u = App\Models\User::find(1);
\$u->password = Illuminate\Support\Facades\Hash::make('admin123');
\$u->save();
echo 'SAVED' . PHP_EOL;
echo 'CHECK=' . (Illuminate\Support\Facades\Hash::check('admin123', \$u->fresh()->password) ? 'OK' : 'BAD') . PHP_EOL;
"
