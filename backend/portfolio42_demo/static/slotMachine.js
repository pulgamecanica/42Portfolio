// window.addEventListener( "load", makeSlotMachine );
// function makeSlotMachine() { 
//     let smc = d3.select( "#slotMachineContent" );
//     let counter = 0;
//     let i = 0;

//     let dt = 4000;

//     smc.selectAll( "svg" ).remove();

//     let svg = smc.append( "svg" ).attr( "id", "slotMachineSvg" )
//         .attr( "width", 300 ).attr( "height", 300 );

//     data = [
//         { content: "9", slogan: "Fourty-Nine" },
//         { content: "♥️", slogan: "For-Love" },
//         { content: "☮️", slogan: "For-Peace" },
//         { content: "1❓", slogan: "Fourty-One?" },
//         { content: "*️⃣", slogan: "For-Everyone" },
//         { content: "2", slogan: "FOURTY TWO" },
//     ];

//     svg.selectAll( "text" ).data( data ).enter().append( "rect" )
//         .attr( "x", d => w * d.x ).attr( "y", d => w * d.y )
//         .attr( "width", w - 1 ).attr( "height", w - 1 )
//         .attr( "fill", d => sc(d.val) );

//     function update() {

//         return d3.shuffle( d3.range( n * n ) ).map( i => {
//             var nb = nbs[ nbs.length * Math.random() | 0 ];
//             var x = (data[i].x + nb[0] + n) % n;
//             var y = (data[i].y + nb[1] + n) % n;
//             data[i].val = data[ y * n + x ].val;
//         } );
//     }

//     d3.interval( function() {
//         update();
//         svg.selectAll( "text" ).data( data )
//             .transition().duration(dt).delay(dt)}, dt );
// }

const items = [
    '🍭',
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
    '😂',
    '🖕',
];
console.log(items);