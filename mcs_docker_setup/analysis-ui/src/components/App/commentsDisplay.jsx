import React from 'react';
import _ from "lodash";
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

const queryName = "getComments"
//TODO:  Update graphql so that we only return the values we need on the final page
const GET_COMMENTS = gql`
    query getComments($test: String!, $block: String!, $submission: String!, $performer: String! ){
        getComments(test: $test, block: $block, submission: $submission, performer: $performer) {
            id
            block
            performer
            submission
            test
            createdDate
            text
            userName
        }
  }`;

class DisplayComments extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            value: 0,
            valueStr: '',
        };
    }
    
    render() {
        return (
            <Query query={GET_COMMENTS} variables={
                {"test": this.props.value.test, 
                "block": this.props.value.block, 
                "submission": this.props.value.subm, 
                "performer": this.props.value.perf
                }} fetchPolicy={this.props.needToRefetch ? 'network-only' : 'cache-first'}>
            {
                ({ loading, error, data }) => {
                    if (loading) return <div>No comments yet</div> 
                    if (error) return <div>Error</div>
                    
                    const comments = data[queryName]
                    const commentsInOrder = _.sortBy(comments, "createdDate");

                    return (
                        <div className="comment-container">
                            <h2>Comments</h2>
                            {commentsInOrder.length > 0 && commentsInOrder.map((item, key) =>
                                <div key={key} className="comment-display"><span className="comment-date">{item.createdDate}:</span>
                                &nbsp;{item.userName} - {item.text}</div>
                            )}

                            {commentsInOrder.length === 0 && 
                                <div>There are no comments yet for this test.</div>
                            }
                        </div>
                    )
                }
            }
            </Query>
        );
    }
}

export {GET_COMMENTS};
export default DisplayComments;