<?php

namespace ManchesterIo;

use Guzzle\Http\Client;

class MollyAdapter
{
    /** @var \Guzzle\Http\Client */
    private $httpClient;

    public function __construct(Client $httpClient)
    {
        $this->httpClient = $httpClient;
        $httpClient->setBaseUrl(\Config::get('manchesterio.mollyBaseUrl'));
        $httpClient->setDefaultOption('headers/Accept', 'application/json');
    }

    public function fetchData($resource)
    {
        return $this->httpClient->get($resource)->send()->json();
    }
}
