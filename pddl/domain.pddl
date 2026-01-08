(define (domain sokoban)
  (:requirements :typing :strips)
  (:types location direction)
  
  (:predicates
    (at-player ?l - location)                  
    (at-box ?l - location)                     
    (clear ?l - location)       
    (adjacent ?from ?to - location ?d - direction)
  )

  (:action move
    :parameters (?from ?to - location ?d - direction)
    :precondition (and 
        (at-player ?from)
        (adjacent ?from ?to ?d) 
        (clear ?to)             
    )
    :effect (and 
        (not (at-player ?from))
        (at-player ?to)
    )
  )

  (:action push
    :parameters (?player-loc ?box-loc ?to-loc - location ?d - direction)
    :precondition (and 
        (at-player ?player-loc)
        (at-box ?box-loc)
        (adjacent ?player-loc ?box-loc ?d)
        (adjacent ?box-loc ?to-loc ?d)
        (clear ?to-loc)
    )
    :effect (and 
        (not (at-player ?player-loc))
        (not (at-box ?box-loc))
        (at-player ?box-loc)
        (at-box ?to-loc)
        
        (clear ?box-loc)        
        (not (clear ?to-loc))   
    )
  )
)