//This file was generated from (Commercial) UPPAAL 4.0.15 rev. CB6BB307F6F681CB, November 2019

/*

*/
//NO_QUERY

/*
Pfitzmann's attack might be undetected
*/
E<> Mteller0.passed_audit

/*
Pfitzmann's attack might be detected
*/
E<> Mteller0.failed_audit

/*
all mix tellers will pass audit ( they are not corrupted )
*/
A[](not (Mteller0.failed_audit or Mteller1.failed_audit or Mteller2.failed_audit) )
