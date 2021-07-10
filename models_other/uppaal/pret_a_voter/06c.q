//This file was generated from (Commercial) UPPAAL 4.0.15 rev. CB6BB307F6F681CB, November 2019

/*

*/
//NO_QUERY

/*
Only coerced Voter can possibly show proof of vote to Coercer
*/
A[] forall(i:v_t)( Coercer.seen[i] imply Voter(i).coerced )

/*
After submitting receipt, Voter can check if it is displayed correctly on the board
*/
Voter(0).received_receipt  --> Voter(0).verification

/*

*/
//NO_QUERY

/*
Every (eligible) Voter can get a ballot form
*/
A[] forall(i:v_t) ( Sys.voting imply Voter(i).has_ballot )

/*

*/
//NO_QUERY

/*

*/
//NO_QUERY

/*
\/\/ A[](Voter(0).received_receipt imply A<>Voter(0).verification)
*/
//NO_QUERY

/*

*/
A<> Sys.voting imply (A<>Voter(0).marked_choice )

/*

*/
A<>( forall(i: int[0,v_total-1]) (curr_phase==1) imply (Voter(i).received_receipt) ) 
