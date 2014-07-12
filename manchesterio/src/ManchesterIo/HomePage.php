<?php

namespace ManchesterIo;

class HomePage
{

    private $twig;

    public function __construct($twig)
    {
        $this->twig = $twig;
    }

    public function render($responseData)
    {
        return $this->twig->render('homepage.twig', $responseData);
    }
}
