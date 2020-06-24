/**
 * Retrieve pre-signed POST data from a dedicated API endpoint.
 * @param selectedFile
 * @returns {Promise<any>}
 */
const getPresignedPostData = selectedFile => {
    return new Promise(resolve => {
        const xhr = new XMLHttpRequest();

        const url = "https://60lrpeo443.execute-api.us-east-1.amazonaws.com/version1/uploadEvaluationSubmission";

        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function () {
            resolve(JSON.parse(this.responseText));
        };
        xhr.send(
            JSON.stringify({
                key: selectedFile.name
            })
        );
    });
};

/**
 * Upload file to S3 with previously received pre-signed POST data.
 * @param presignedPostData
 * @param file
 * @returns {Promise<any>}
 */
const uploadFileToS3 = (presignedPostData, file) => {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("PUT", presignedPostData.url, true);
        xhr.setRequestHeader("Content-Type", "multipart/form-data");
        xhr.onload = function () {
            this.status === 200 ? resolve() : reject(this.responseText);
        };
        xhr.onerror = function (error) {
            $("#fileUploadStatus").text(error);
            console.log("An error occurred during the upload!");
        };
        xhr.send(file); 
    });
};

const e = React.createElement;

class FileUploadButton extends React.Component {
    constructor(props) {
        super(props);
        this.state = { file: undefined, fileName: ""}

        this.onFormSubmit = this.onFormSubmit.bind(this)
        this.handleChange = this.handleChange.bind(this)
    }

    onFormSubmit(e) {
        e.preventDefault() 
        $("#fileUploadStatus").text("");
        
        try {
            Object.defineProperty(this.state.file, 'name', {
                writable: true,
                value: (new Date).toISOString() + "_" + this.state.file.name
            });

            getPresignedPostData(this.state.file)
                .then( response => {
                    uploadFileToS3(response, this.state.file)
                        .then (response => {
                            console.log("Success!");
                            $("#fileUploadStatus").text("File Upload Success!");
                        })
                })
        } catch (e) {
            console.log("An error occurred!", e.message);
            $("#fileUploadStatus").text("Error uploading the file. " + e.message);
        }
    }

    handleChange(e) {
        this.setState({ file: e.target.files[0], fileName: e.target.files[0].name });
    }

    render() {
        return (
            React.createElement('form', { className: 'FileForm', onSubmit: this.onFormSubmit },
                React.createElement('input', {
                    type: 'file',
                    name: this.state.fileName,
                    onChange: this.handleChange
                }),
                React.createElement('button', { type: 'submit' }, "Upload")
            )
        )
    }
}

const domContainer = document.querySelector('#FileUploadButton');
ReactDOM.render(e(FileUploadButton), domContainer);