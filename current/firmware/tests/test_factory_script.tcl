# Execute the production Tcl script against OpenOCD command/WRP-block models.
# No hardware is accessed. Values model STM32F042 and its four-page WRP groups.
proc init {} {}
proc reset {args} {}
proc shutdown {} {}
proc echo {args} {}
proc mrw {address} {
    if {$address == 0x40015800} {return $::device}
    if {$address == 0x40022020} {return $::wrp}
    error "Unexpected register"
}
proc mrh {address} {
    if {$address == 0x1ffff7cc} {return $::flash_size}
    if {$address == 0x1ffff808} {return [expr {((255 ^ $::wrp)<<8) | $::wrp}]}
    error "Unexpected halfword"
}
proc verify_image {path} {
    if {!$::programmed || ![file exists $path]} {error "Missing image/program step"}
}
proc flash {op args} {
    if {$op == "probe"} {return}
    if {$op == "write_image"} {set ::programmed 1;return}
    if {$op == "protect"} {
        lassign $args bank first last on
        if {$bank != 0 || $on != "on" || $last > 7} {error "Unexpected protection arguments"}
        for {set i $first} {$i <= $last} {incr i} {set ::wrp [expr {$::wrp & ~(1<<$i)}]}
        return
    }
    error "Unexpected flash operation"
}
foreach scenario {fresh already_protected wrong_device wrong_size other_protection} {
    set device 0x445;set flash_size 32;set wrp 255;set programmed 0
    switch $scenario {
        already_protected {set wrp 252}
        wrong_device {set device 0x444}
        wrong_size {set flash_size 64}
        other_protection {set wrp 127}
    }
    set failed [catch {source tools/program_factory.tcl} reason]
    if {$scenario == "fresh"} {
        if {$failed || !$programmed || $wrp != 252} {error "Protection script failed: $reason / WRP $wrp"}
    } elseif {!$failed || $programmed} {error "$scenario must refuse before writing"}
}
puts "factory script: 5 modeled OpenOCD cases pass; only 8 KiB boot protected, unexpected targets refused"
