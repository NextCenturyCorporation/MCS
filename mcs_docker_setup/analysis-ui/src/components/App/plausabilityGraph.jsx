import React from 'react';
import {ResponsiveLine} from '@nivo/line';
import _ from 'lodash';
import $ from 'jquery';

const MyResponsiveLine = ({ data, state, onClickHandler}) => (
    <ResponsiveLine
        data={data}
        margin={{ top: 20, right: 175, bottom: 30, left: 80 }}
        xScale={{ type: 'linear', min: 1, max: 100}}
        yScale={{ type: 'linear', min: 0, max: 1.1}}
        axisBottom={{
            orient: 'bottom',
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Frame',
            legendOffset: 36,
            legendPosition: 'middle',
            tickValues: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        }}
        axisLeft={{
            orient: 'left',
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Plausibility',
            legendOffset: -40,
            legendPosition: 'middle',
            tickValues: [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        }}
        colors={{ scheme: 'dark2' }}
        enablePoints={false}
        pointSize={10}
        pointColor={{ theme: 'background' }}
        pointBorderWidth={2}
        pointBorderColor={{ from: 'serieColor', modifiers: [] }}
        pointLabel="y"
        pointLabelYOffset={-12}
        useMesh={true}
        legends={[
            {
                anchor: 'top-right',
                direction: 'column',
                justify: false,
                reverse: true,
                translateX: 100,
                translateY: 0,
                itemsSpacing: 0,
                itemDirection: 'left-to-right',
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: 'circle',
                symbolBorderColor: 'rgba(0, 0, 0, .5)',
                onClick: onClickHandler,
                effects: [
                    {
                        on: 'hover',
                        style: {
                            itemBackground: 'rgba(0, 0, 0, .03)',
                            itemOpacity: 1
                        }
                    }
                ]
            }
        ]}
        markers={[
            {
                axis: 'x',
                value: state.value,
                lineStyle: {
                    stroke: 'blue',
                }
            }
        ]}
    />
)

class PlausabilityGraph extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentData: $.extend(true, [], _.reverse(this.props.pointsData))
        };
    }

    updateCurrentData = (sceneToggle) => {
        let tempData = this.state.currentData;
        let sceneArr = sceneToggle.id.split(" ")
        let sceneNumber = sceneArr[1];

        for(let i=0; i < tempData.length; i++) {
            if(tempData[i].id === sceneToggle.id) {
                if(tempData[i].data.length > 0) {
                    tempData[i].data = [];
                    $("#scene_image_" + sceneNumber).css({opacity: .1});
                } else {
                    for(let j=0; j < this.props.pointsData.length; j++) {
                        if(this.props.pointsData[j].id === sceneToggle.id) {
                            tempData[i].data = $.extend(true, [], this.props.pointsData[j].data);
                            $("#scene_image_" + sceneNumber).css({opacity: 1});
                        }
                    }
                }
            }
        }
        this.setState({ currentData: tempData });
    }

    render() {
        return (
            <div style={{ height: '300px', width: '100%' }}>
                <MyResponsiveLine data={this.state.currentData} state={this.props.state} onClickHandler={this.updateCurrentData}/>
            </div>       
        )
    }
}

export default PlausabilityGraph;