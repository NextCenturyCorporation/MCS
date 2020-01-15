import React from 'react';
import Slider from 'rc-slider';
import $ from 'jquery';

class SceneSlider extends React.Component {

    togglePlayPause = () => {
        $( "#sliderPlay" ).toggleClass( "slider-play-pause-hide" );
        $( "#sliderPause" ).toggleClass( "slider-play-pause-hide" );
    }

    onSliderChange = (value) => {
        this.props.onChange(value);
    };

    restartSlider = () => {
        this.props.onChange(1);

        if($( "#sliderPlay" ).hasClass( "slider-play-pause-hide" )) {
            this.togglePlayPause();
            clearInterval(window.sliderInterval);
        }
    };

    frameForward = () => {
        if(this.props.state.value <= 99 ) {
            this.props.onChange(parseInt(this.props.state.value) + 1);
        }
    };

    frameBackward = () => {
        if(this.props.state.value > 1) {
            this.props.onChange(parseInt(this.props.state.value) - 1);
        }
    };

    playScene = () => {
        this.togglePlayPause();

        let that = this;

        window.sliderInterval = setInterval(function(){
            if(that.props.state.value >= 100 ) {
                clearInterval(window.sliderInterval);
                that.togglePlayPause();
            } else {
                that.props.onChange(parseInt(that.props.state.value) + 1);
            }
        }, 80);
    };

    pauseScene = () => {
        this.togglePlayPause();
        clearInterval(window.sliderInterval);
    };

    render() {
        
        return (
            <div className="scene-control-container">
                <div>Scene Controls:</div>
                <div className="scene-control-background">
                    <div onClick={this.restartSlider}><i className='material-icons' style={{fontSize: '24px'}}>replay</i></div>
                    <div id="sliderPlay" onClick={this.playScene}><i className='material-icons' style={{fontSize: '24px'}}>play_arrow</i></div>
                    <div id="sliderPause" onClick={this.pauseScene} className="slider-play-pause-hide"><i className='material-icons' style={{fontSize: '24px'}}>pause</i></div>
                    <div onClick={this.frameBackward}><i className='material-icons' style={{fontSize: '24px'}}>fast_rewind</i></div>
                    <div className="slider-holder"><Slider value={parseInt(this.props.state.value)} onChange={this.onSliderChange} min={1}/></div>
                    <div onClick={this.frameForward}><i className='material-icons' style={{fontSize: '24px'}}>fast_forward</i></div>
                </div>
                <div className="slider-current-frame">Frame: {this.props.state.value}</div>
            </div>
        );
    }
}

export default SceneSlider;