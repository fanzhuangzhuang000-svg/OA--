#!/bin/bash
cd /var/www/oa-api
sudo -u www-data php -r "
require 'vendor/autoload.php';
\$app = require 'bootstrap/app.php';
\$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
echo 'NEW_HASH=' . Illuminate\Support\Facades\Hash::make('admin123') . PHP_EOL;
\$u = App\Models\User::find(1);
echo 'USER_PASSWORD=' . (\$u ? \$u->password : 'NOUSER') . PHP_EOL;
echo 'CHECK=' . (Illuminate\Support\Facades\Hash::check('admin123', \$u->password) ? 'OK' : 'BAD') . PHP_EOL;
"
