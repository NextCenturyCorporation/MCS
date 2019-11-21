import React from 'react';

class EvalHeader extends React.Component {
    render() {
        return (
            <div className="header">
                <div className="title">Performer: { this.props.state.perf }</div>
                <div className="title">Submission: { this.props.state.subm }</div>
                <div className="title">Block: { this.props.state.block }</div>
                <div className="title">Test: { this.props.state.test }</div>
            </div>
        );
    }
}

export default EvalHeader;
