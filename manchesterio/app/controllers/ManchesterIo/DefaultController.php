<?php

namespace ManchesterIo;

class DefaultController extends \Controller
{

    public function defaultAction()
    {
        return \View::make('default');
    }
}
