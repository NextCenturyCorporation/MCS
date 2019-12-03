import React from 'react';
import Dropdown from 'react-dropdown';
import 'react-dropdown/style.css';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import _ from "lodash";

const GET_FIELD_AGG = gql`
    query getFieldAggregation($fieldName: String!){
        getFieldAggregation(fieldName: $fieldName) {
            key
        }
  }`;

class HeaderDropdown extends React.Component {
    render() {
        return (
            <Query query={GET_FIELD_AGG} variables={{"fieldName": this.props.fieldName}}>
            {
                ({ loading, error, data }) => {
                    let dropdownOptions = [];
                    let that = this;

                    if(data !== undefined) {
                        dropdownOptions = _.map(data["getFieldAggregation"], 'key');
                    }

                    function headerOnChange(item) {
                        that.props.state[that.props.stateName] = item.value;

                        const urlBasePath = window.location.href.split('?')[0];
                        const params = "?perf=" + that.props.state["perf"] + "&subm=" + that.props.state["subm"] + "&block=" + that.props.state["block"] + "&test=" + that.props.state["test"];

                        window.location = urlBasePath + params;
                    }

                    return (
                        <Dropdown options={dropdownOptions} onChange={headerOnChange} value={this.props.defaultOption}/>
                    )
                }
            }
            </Query>
        );
    }
}

class EvalHeader extends React.Component {
    render() {
        return (
            <div className="header">
                <div className="title">
                    <div className="header-dropdown-title">Performer: </div>
                    <HeaderDropdown fieldName={"performer"} stateName={"perf"} defaultOption={this.props.state.perf} className="header-dropdown" state={this.props.state}/>
                </div>
                <div className="title">
                    <div className="header-dropdown-title">Submission: </div>
                    <HeaderDropdown fieldName={"submission"} stateName={"subm"} defaultOption={this.props.state.subm} className="header-dropdown" state={this.props.state}/>
                </div>
                <div className="title">
                    <div className="header-dropdown-title">Block: </div>
                    <HeaderDropdown fieldName={"block"} stateName={"block"} defaultOption={this.props.state.block} className="header-dropdown" state={this.props.state}/>
                </div>
                <div className="title">
                    <div className="header-dropdown-title">Test: </div>
                    <HeaderDropdown fieldName={"test"} stateName={"test"} defaultOption={this.props.state.test} className="header-dropdown" state={this.props.state}/>
                </div>
            </div>
        );
    }
}

export default EvalHeader;
