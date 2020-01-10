import React from 'react';

const ImageHolder = ({currentEval, state, imagesBucket, scene}) => {
    const styles = {};

    if(parseInt(currentEval.ground_truth) === 0) {
        styles["border"] = "2px solid red";
    } else {
        styles["border"] = "2px solid white";
    }

    const url = imagesBucket + currentEval["block"] + "/" + currentEval["test"] + "/" + scene + "/scene/scene_" + state.value + ".png"
  
    return (
      <img id={"scene_image_" + scene} className="scene-image" style={styles} src={url} alt=""/>
    );
}

const LocationHolder = ({currentEval, state}) => {
    const styles = {
        top: currentEval["location_y"],
        left: currentEval["location_x"]
    };

    if(currentEval["location_frame"] === parseInt(state.value)) {
        styles["display"] = "inline";
    } else {
        styles["display"] = "none";
    }

    return (
        <div style={styles} className="location-dot"></div>
    );
}

class SceneImage extends React.Component {

    render() {
        
        return (
            <div>
                <div className="scene-info-container">
                    <span className="scene-info-holder"><b>Complexity:</b> {this.props.evals[0].complexity}</span>
                    <span className="scene-info-holder"><b>Occluders:</b> {this.props.evals[0].occluder}</span>
                    <span className="scene-info-holder"><b>Number of Objects:</b> {this.props.evals[0].num_objects}</span>
                    <span className="scene-info-holder-note">(These values are the same across all scenes, and represent the highest value a scene could have)</span>
                </div>
                <div className="scene-image-container">
                    {this.props.evals.map((item, key) =>
                        <div key={"scene_image_" + key}>
                            <div className="sceneinfo">Scene: {key+1}</div>
                            <div className="scene-image-container-holder">
                                <ImageHolder currentEval={item} state={this.props.state} imagesBucket={this.props.imagesBucket} scene={key+1}/>
                                <LocationHolder currentEval={item} state={this.props.state}/>
                            </div>
                            <div className="sceneScore">Plausibility: {item.plausibility}<br/>Loc. Frame (x,y): {item.location_frame} ({item.location_x}, {item.location_y})<br/>Ground Truth: {item.ground_truth}</div>
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

export default SceneImage;