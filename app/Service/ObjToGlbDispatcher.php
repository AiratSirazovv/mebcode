<?php

declare(strict_types=1);

namespace App\Service;

use Illuminate\Support\Facades\Redis;

class ObjToGlbDispatcher
{
    private const string KEY = 'model:status:';
    private const string QUEUE = 'model:blender';

    /**
     * @throws \JsonException
     */
    public function dispatch(string $id, string $fileName): void
    {
        Redis::transaction(function (\Redis $tx) use ($id, $fileName) {
            $tx->hMset(self::KEY.$id, [
                'stage' => 'blender',
                'status' => 'queued',
            ]);

            $payload = $this->getPayload($id, $fileName);
            $tx->lPush(self::QUEUE, $payload);
        });
    }

    /**
     * @throws \JsonException
     */
    private function getPayload(string $id, string $fileName): string
    {
        $payload = [
            'id' => $id,
            'fileName' => $fileName,
            'ts' => time(),
        ];

        return \json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    }
}
