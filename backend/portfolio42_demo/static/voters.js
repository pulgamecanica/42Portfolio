let contrast = (color) => { return color != "black" ? "black" : "white" };

// Array defining all the possible neighbors
const nbs = [ [0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1] ];

const darkblue = "#314050";
const washedblue = "#58b7ba";
const lightblue = "#a5b2e1";
const white = "white";
const black = "black";
const peach = "#e0aea5";
const gray = "#2a2d38";

function Voters() {
    this.colors = [ darkblue, washedblue, white, black, peach, gray];
    this.windowWidth = parseInt(getComputedStyle(document.body).width, 10);
    this.windowHeight = parseInt(getComputedStyle(document.body).height, 10);

    // Choose the biggest size in order to always cover the window
    this.svgSize = Math.max(this.windowWidth, this.windowHeight);

    // Select element which holds the svg
    this.bg = d3.select( "#background-arena" );

    // Create the initial svg
    this.svg = this.bg.append( "svg" ).attr( "id", "voters" )
        .attr( "width", this.svgSize ).attr( "height", this.svgSize );

    this.graphSvg = d3.select( "#votersStats" ).append( "svg" ).attr( "id", "voters" ).attr( "opacity", "0.3" );

    // The number of square divisions
    this.n = 150;

    // The width of each square division
    this.w = this.svgSize / this.n;

    // The duration of the animation in miliseconds
    this.dt = 3000;

    // Scale to choose colors
    this.sc = d3.scaleQuantize().range( this.colors );

    this.graphSize = Math.floor(this.svgSize * 0.05);
    this.arcMkr = d3.arc()
        .innerRadius(Math.floor(this.graphSize * 0.0))
        .outerRadius(Math.floor(this.graphSize * 0.4))
        .cornerRadius(5)
}

Voters.prototype = {
    drawVoters: function() {
        this.svg.selectAll( "rect" ).data( this.data ).enter().append( "rect" )
            .attr( "x", d => this.w * d.x ).attr( "y", d => this.w * d.y )
            .attr( "width", this.w + 1 ).attr( "height", this.w + 1 )
            .attr( "fill", d => d.color );
    },

    update: function() {
        /**
         * Shuffle all the divisions, for each division
         * Select a neighbor randomly 'nb'
         * Calculate the coordinates of the neighbor
         * Change the neighbor color
         * Repaint the divisions, with a smooth transition
         **/
        d3.shuffle( d3.range( this.n * this.n ) ).map( i => {
            var nb = nbs[ nbs.length * Math.random() | 0 ];
            var x = (this.data[i].x + nb[0] + this.n) % this.n;
            var y = (this.data[i].y + nb[1] + this.n) % this.n;
            this.data[i].color = this.data[ y * this.n + x ].color;
        } );
        this.svg.selectAll( "rect" ).data( this.data )
            .transition().duration(this.dt).delay((d, i)=>i * 0.25 * this.dt / (this.n * this.n))
            .attr( "fill", d => d.color ) 
    },

    colorIndex: function(color) {
        for (let i = 0; i < this.colors.length; i++)
            if (color == this.colors[i])
                return i;
        return -1;
    },

    drawGraph: function() {
        let graphData = this.colors.map( color => {
            return ({ "color": color, "count": 0, "portion": 0});
        });
        // Count the number of divisions for every color
        for (let i = 0; i < this.data.length; i++)
            graphData[this.colorIndex(this.data[i].color)].count += 1;
        // Set the % of each color => color.portion
        for (let i = 0; i < graphData.length; i++)
            graphData[i].portion = ((graphData[i].count * 100) / (this.n * this.n)).toFixed(2);

        let pie = d3.pie().value( d => d.count ).padAngle( 0.02 )( graphData );

        this.graphSvg.selectAll( "g" ).remove();

        let g = this.graphSvg.append( "g" ).attr( "transform", "translate(" + this.graphSize + ", 50)")

        g.selectAll("path").data( pie ).enter().append( "path" )
            .attr( "d", this.arcMkr ).attr( "fill", d=>d.data.color ).attr( "stroke", "gray" );

        g.selectAll("text").data( pie ).enter().append( "text" )
            .text( d => d.data.portion + "%" )
            .attr( "x", d => this.arcMkr.innerRadius(Math.floor(this.graphSize * 0.2)).centroid(d)[0] )
            .attr( "y", d => this.arcMkr.innerRadius(Math.floor(this.graphSize * 0.2)).centroid(d)[1] )
            .attr( "font-family", "sans-serif" ).attr("font-size", Math.floor(this.graphSize * 0.075))
            .attr( "text-anchor", "middle" )
            .attr( "fill", d => contrast(d.data.color) )
    },

    init: function() {
        this.data = d3.range(this.n * this.n)
            .map( d => { return { x: d % this.n, y: d / this.n | 0,
                                    color: this.sc(Math.random()) } } );
        this.drawVoters();
        this.update();
        this.drawGraph();
    }
};

window.addEventListener( "load", makeVoters );

function makeVoters() { 
    let v = new Voters();
    v.init();
    d3.interval( function() {
        v.update();
        v.drawGraph();
        }, v.dt );
}