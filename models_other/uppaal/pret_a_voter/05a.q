//This file was generated from (Commercial) UPPAAL 4.0.15 rev. CB6BB307F6F681CB, November 2019

/*

*/
E<> Auditor.mix_fail

/*

*/
A<>( forall(i: int[0,v_total-1]) (curr_phase==1) imply (Voter(i).received_receipt) ) 
