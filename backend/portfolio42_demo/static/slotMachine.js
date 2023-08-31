function SlotMachine(duration = 1) {
	this.items = [
	    '2',
	    '❌',
	    '⛄️',
	    '🦄',
	    '🍌',
	    '💩',
	    '👻',
	    '😻',
	    '💵',
	    '🤡',    
	    '🦖',
	    '🍎',
	    '?',
	];
	this.duration = duration;
	this.openings = d3.selectAll('.sm-opening');
	this.openingHeight = parseInt(getComputedStyle(this.openings.node()).height, 10);
}

SlotMachine.prototype = {
	init: function() {
		this.openings.selectAll( "div" ).remove();
		this.openings.append( "div" ).attr( "class", "options" )
			.attr( "style", `transform: translateY(-${this.openingHeight * (this.items.length - 1)}px);` )
			.selectAll( "div" ).data( this.items ).enter().append( "div" )
			.text( d => d ).attr( "class", "option" );

	},

	spin: function() {
		for (opt of this.openings.selectAll( ".option" ).nodes() )
			opt.style.filter = 'blur(1px)';
		this.openings.selectAll( ".options" ).attr( "style", `transform: translateY(0px);transition-duration: ${this.duration > 0 ? this.duration : 1}s;` );
		setTimeout(() => {
			for (opt of this.openings.selectAll( ".option" ).nodes() )
			opt.style.filter = 'blur(0px)';
		}, this.duration * 1000);
		
	},
}

window.addEventListener( "load", () => {
	let sm = new SlotMachine();
	sm.init();
	d3.interval( function() {
		sm.init();
    	setTimeout(() => {
    		sm.spin();
		}, 1000);
	}, 4000);
	
});
