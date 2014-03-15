<?php

namespace ManchesterIo;

use Guzzle\Http\Exception\ClientErrorResponseException;

class DefaultController extends \Controller
{
    /** @var \ManchesterIo\MollyAdapter */
    private $molly;

    public function __construct(MollyAdapter $molly)
    {
        $this->molly = $molly;
    }

    public function defaultAction($path = '')
    {
        try {
            $data = $this->molly->fetchData($path);
        } catch (ClientErrorResponseException $ex) {
            if ($ex->getResponse()) {
                \App::abort($ex->getResponse()->getStatusCode());
            } else {
                throw $ex;
            }
        }
        return \View::make('default', array('data' => $data));
    }
}
