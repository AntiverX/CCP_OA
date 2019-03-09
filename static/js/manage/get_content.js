class Table extends React.Component {

    row() {
        return (
            <tr>
                <th scope="col">1</th>
                <td>20018-2019-1</td>
                <td>2019-02-27</td>
                <td>2019-06-01</td>
            </tr>
        );
    }


    table = () => {
        return (
            <table className="table mt-2" id="table">
                <thead>
                <tr>
                    <th scope="col">序号</th>
                    <th scope="col">学期名称</th>
                    <th scope="col">学期开始日期</th>
                    <th scope="col">学期结束日期</th>
                </tr>
                </thead>
                <this.row/>
                <tbody>
                </tbody>
            </table>
        );
    }

    render() {
        return <this.table/>;
    }
}


const element = <Table/>;
ReactDOM.render(
    element,
    document.getElementById('table')
);
