<?php

namespace App\Console\Commands;

use App\Service\ObjToGlbDispatcher;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;

#[Signature('app:push')]
#[Description('Command description')]
class PushCommand extends Command
{
    public function handle(ObjToGlbDispatcher $dispatcher)
    {
        $dispatcher->dispatch();
    }
}
