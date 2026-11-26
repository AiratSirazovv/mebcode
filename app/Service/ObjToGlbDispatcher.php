<?php

declare(strict_types=1);

namespace App\Service;


use Illuminate\Support\Facades\Redis;

class ObjToGlbDispatcher
{
    public function dispatch(): void
    {
        Redis::transaction(function ( $redis) {
            $redis->incr('user_visits', 15);
            $redis->incr('total_visits', 1);
        });
    }
}
